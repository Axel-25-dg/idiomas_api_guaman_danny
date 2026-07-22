"""
LiveSessionConsumer — WebSocket para señalización WebRTC (Multi-usuario + Redis)
=============================================================================
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

        # Registrar en la "Pizarra Central" (Redis)
        is_teacher = getattr(self.user.role, 'name', '') == 'teacher' if hasattr(self.user, 'role') else False
        await self._add_participant(is_teacher)

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        print(f"--> CONECTADO CON ÉXITO: {self.user.username} unido.")

        # Notificar al resto que llegó alguien (CRÍTICO para Multi-usuario)
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':       'user_joined',
                'user_id':    self.user.id,
                'username':   self.user.username,
                'is_teacher': is_teacher,
            },
        )

        # Enviar lista de participantes actuales al recién conectado
        participants_data = await self._get_participants()
        
        participants_list = [
            {
                'user_id': uid,
                'username': p_data.get('username', ''),
                'is_teacher': p_data.get('is_teacher', False)
            }
            for uid, p_data in participants_data.items()
            if str(uid) != str(self.user.id)
        ]
        
        print(f"--> Enviando lista de otros participantes: {[p['user_id'] for p in participants_list]}\n")
        await self.send_json({'type': 'participants', 'users': participants_list})

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

            # Logs de señales para ver si los Offer/Answer viajan
            if event_type in ('offer', 'answer', 'ice_candidate'):
                target = data.get('target', 'BROADCAST')
                print(f"   [SIGNAL] {event_type} de {self.user.id} para {target}")
                await self._relay_signal(event_type, data)
            elif event_type == 'leave_room':
                await self.close()
        except Exception as e:
            print(f"   [ERROR RECEIVE] {e}")

    # ── Relay de señales WebRTC Targeteadas ──────────────────────────────────
    async def _relay_signal(self, signal_type, data):
        target_id = data.get('target')
        payload   = {
            'type': signal_type,
            'from': self.user.id,
            'sdp':  data.get('sdp'),
            'candidate': data.get('candidate'),
        }

        if target_id:
            # Enviar solo a una persona específica (Peer-to-Peer)
            participants = await self._get_participants()
            target_data = participants.get(str(target_id))
            target_channel = target_data.get('channel') if isinstance(target_data, dict) else target_data
            if target_channel:
                await self.channel_layer.send(target_channel, payload)
            else:
                await self.send_json({'type': 'error', 'detail': 'Destinatario no encontrado en la sala.'})
        else:
            # Si no hay target, enviar a todos (usar con cuidado)
            await self.channel_layer.group_send(self.room_name, payload)

    # ── Handlers del grupo ───────────────────────────────────────────────────
    async def user_joined(self, event):
        if event['user_id'] != self.user.id:
            await self.send_json({
                'type': 'user_joined', 
                'user_id': event['user_id'], 
                'username': event['username'],
                'is_teacher': event.get('is_teacher', False)
            })

    async def user_left(self, event):
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
    def _add_participant(self, is_teacher=False):
        participants = cache.get(self.cache_key, {})
        participants[str(self.user.id)] = {
            'channel': self.channel_name,
            'username': self.user.username,
            'is_teacher': is_teacher
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
