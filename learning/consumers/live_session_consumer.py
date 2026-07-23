"""
LiveSessionConsumer — WebSocket para señalización WebRTC (Multi-usuario + Redis)
=============================================================================
FIXES aplicados:
  1. 'participants' ahora envía objetos completos {user_id, username, is_teacher}
     en lugar de solo una lista de IDs.
  2. Se añadió soporte para 'chat_message': retransmite al grupo con el username.
  3. Se añadió soporte para 'end_session': retransmite a todos en la sala.
  4. Se añadió soporte para 'screen_share_status': retransmite a todos.
  5. Se añadió soporte para 'request_screen_share': retransmite al grupo.
  6. Se añadió soporte para 'grant_screen_share': se envía solo al usuario destino.
  7. 'user_joined' ahora incluye el campo 'is_teacher' del usuario.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from asgiref.sync import sync_to_async


class LiveSessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user       = self.scope['user']
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_name  = f'session_{self.session_id}'
        self.cache_key  = f'live_participants_{self.session_id}'

        print(f"\n================ [WS INTENTO DE CONEXIÓN] ================")
        print(f"--> Usuario: {self.user} | ID: {getattr(self.user, 'id', 'None')}")
        print(f"--> Sesión ID: {self.session_id} | Sala: {self.room_name}")

        if not self.user or not self.user.is_authenticated:
            print("--> RECHAZADO [Error 4001]: Usuario no autenticado.\n")
            await self.close(code=4001)
            return

        session_ok = await self._session_is_available()
        if not session_ok:
            print("--> RECHAZADO [Error 4404]: La sesión no existe o no está activa.\n")
            await self.close(code=4404)
            return

        # Determinar si el usuario es profesor/admin para incluirlo en sus datos
        self.is_teacher = await self._is_teacher_or_admin()

        # 1. Registrar en la "Pizarra Central" (Redis) con datos completos
        await self._add_participant()

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        print(f"--> CONECTADO CON ÉXITO: {self.user.username} unido.")

        # 2. Notificar al resto que llegó alguien (CRÍTICO para Multi-usuario)
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':       'user_joined',
                'user_id':    self.user.id,
                'username':   self.user.username,
                'is_teacher': self.is_teacher,
            },
        )

        # 3. Enviar lista de participantes actuales al que acaba de entrar
        #    FIX: enviamos objetos completos, no solo IDs
        participants = await self._get_participants()
        other_users = [
            {
                'user_id':    int(uid),
                'username':   data.get('username', f'Usuario {uid}'),
                'is_teacher': data.get('is_teacher', False),
            }
            for uid, data in participants.items()
            if str(uid) != str(self.user.id)
        ]

        print(f"--> Enviando lista de otros participantes: {[u['username'] for u in other_users]}\n")
        await self.send_json({'type': 'participants', 'participants': other_users})

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            print(f"--> DESCONECTADO: {self.user.username} salió de la sala.")
            await self._remove_participant()
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
            await self.channel_layer.group_send(
                self.room_name,
                {'type': 'user_left', 'user_id': self.user.id},
            )

    async def receive(self, text_data):
        try:
            data       = json.loads(text_data)
            event_type = data.get('type')

            print(f"   [RECEIVE] tipo={event_type} de user_id={self.user.id}")

            # ── Señalización WebRTC (targeteada por user_id) ──────────────────
            if event_type in ('offer', 'answer', 'ice_candidate'):
                target = data.get('target', 'BROADCAST')
                print(f"   [SIGNAL] {event_type} de {self.user.id} para {target}")
                await self._relay_signal(event_type, data)

            # ── Chat: retransmitir a todos en la sala ──────────────────────────
            elif event_type == 'chat_message':
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type':      'chat_message',
                        'user_id':   self.user.id,
                        'username':  self.user.username,
                        'message':   data.get('message', ''),
                        'timestamp': data.get('timestamp', ''),
                    }
                )

            # ── Finalizar sesión: retransmitir a todos ────────────────────────
            elif event_type == 'end_session':
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type':   'end_session',
                        'reason': data.get('reason', 'teacher_ended'),
                    }
                )

            # ── Compartir pantalla: estado (is_sharing true/false) ────────────
            elif event_type == 'screen_share_status':
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type':       'screen_share_status',
                        'user_id':    self.user.id,
                        'username':   self.user.username,
                        'is_sharing': data.get('is_sharing', False),
                    }
                )

            # ── Solicitud de permiso para compartir pantalla ──────────────────
            elif event_type == 'request_screen_share':
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type':     'request_screen_share',
                        'user_id':  self.user.id,
                        'username': self.user.username,
                    }
                )

            # ── Conceder / revocar permiso (solo al usuario target) ───────────
            elif event_type == 'grant_screen_share':
                target_user_id = data.get('target_user_id')
                allowed        = data.get('allowed', False)
                if target_user_id:
                    participants = await self._get_participants()
                    target_data  = participants.get(str(target_user_id))
                    if target_data and 'channel' in target_data:
                        await self.channel_layer.send(
                            target_data['channel'],
                            {
                                'type':           'grant_screen_share',
                                'target_user_id': target_user_id,
                                'allowed':        allowed,
                            }
                        )

            elif event_type == 'leave_room':
                await self.close()

        except Exception as e:
            print(f"   [ERROR RECEIVE] {e}")

    # ── Relay de señales WebRTC Targeteadas ──────────────────────────────────
    async def _relay_signal(self, signal_type, data):
        target_id = data.get('target')
        payload   = {
            'type':      signal_type,
            'from':      self.user.id,
            'sdp':       data.get('sdp'),
            'candidate': data.get('candidate'),
        }

        if target_id:
            # Enviar solo a una persona específica (Peer-to-Peer)
            participants = await self._get_participants()
            target_data  = participants.get(str(target_id))
            if target_data and 'channel' in target_data:
                await self.channel_layer.send(target_data['channel'], payload)
        else:
            # Si no hay target, enviar a todos (usar con cuidado)
            await self.channel_layer.group_send(self.room_name, payload)

    # ── Handlers del grupo (uno por cada 'type' enviado al group_send) ───────

    async def user_joined(self, event):
        """Notifica a todos (excepto al propio usuario) que alguien entró."""
        if event['user_id'] != self.user.id:
            await self.send_json(event)

    async def user_left(self, event):
        """Notifica a todos que alguien salió."""
        await self.send_json(event)

    async def chat_message(self, event):
        """Entrega el mensaje de chat a este cliente."""
        if event.get('user_id') != self.user.id:
            await self.send_json(event)

    async def end_session(self, event):
        """Notifica a todos que la sesión fue finalizada."""
        await self.send_json(event)

    async def screen_share_status(self, event):
        """Notifica a todos el estado de compartir pantalla."""
        if event.get('user_id') != self.user.id:
            await self.send_json(event)

    async def request_screen_share(self, event):
        """Notifica al grupo (el profesor lo recibirá) la solicitud."""
        if event.get('user_id') != self.user.id:
            await self.send_json(event)

    async def grant_screen_share(self, event):
        """Entrega la respuesta de permiso al usuario específico."""
        await self.send_json(event)

    async def offer(self, event):
        if event.get('from') != self.user.id:
            await self.send_json(event)

    async def answer(self, event):
        if event.get('from') != self.user.id:
            await self.send_json(event)

    async def ice_candidate(self, event):
        if event.get('from') != self.user.id:
            await self.send_json(event)

    # ── Helpers de Cache (Redis) ─────────────────────────────────────────────
    @sync_to_async
    def _add_participant(self):
        participants = cache.get(self.cache_key, {})
        participants[str(self.user.id)] = {
            'channel':    self.channel_name,
            'username':   self.user.username,
            'is_teacher': getattr(self, 'is_teacher', False),
        }
        cache.set(self.cache_key, participants, timeout=7200)

    @sync_to_async
    def _remove_participant(self):
        participants = cache.get(self.cache_key, {})
        participants.pop(str(self.user.id), None)
        if not participants:
            cache.delete(self.cache_key)
        else:
            cache.set(self.cache_key, participants, timeout=7200)

    @sync_to_async
    def _get_participants(self):
        return cache.get(self.cache_key, {})

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content, default=str))

    @database_sync_to_async
    def _session_is_available(self):
        from learning.models import LiveSession
        return LiveSession.objects.filter(
            pk=self.session_id, status__in=('scheduled', 'live')
        ).exists()

    @database_sync_to_async
    def _is_teacher_or_admin(self):
        """Verifica si el usuario es profesor o admin para marcar is_teacher."""
        user = self.user
        role = getattr(user, 'role', None)
        if role in ('teacher', 'admin'):
            return True
        if getattr(user, 'is_teacher', False):
            return True
        # Verificar si es el profesor de esta sesión
        from learning.models import LiveSession
        return LiveSession.objects.filter(
            pk=self.session_id,
            teacher=user
        ).exists()
