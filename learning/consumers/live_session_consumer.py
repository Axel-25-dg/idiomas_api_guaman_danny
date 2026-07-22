"""
LiveSessionConsumer — WebSocket para señalización WebRTC (Producción con Redis)
=============================================================================
ws/live-session/<session_id>/

Flujo WebRTC estándar (señalización via WebSocket):
  1. Participante A se conecta  → broadcast 'user_joined'
  2. A envía 'offer'            → se reenvía a B
  3. B responde 'answer'        → se reenvía a A
  4. A y B intercambian 'ice_candidate' entre sí
  5. Conexión P2P establecida (canal de datos/video/audio)

Esta versión utiliza la Cache de Django (Redis) para gestionar la lista de participantes
de forma global entre múltiples workers/servidores.
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

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        if not await self._session_is_available():
            await self.close(code=4404)
            return

        # 1. Registrar en la "Pizarra Central" (Redis/Cache)
        await self._add_participant()

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        # Notificar al resto que llegó alguien
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':     'user_joined',
                'user_id':  self.user.id,
                'username': self.user.username,
            },
        )

        # Enviar lista de participantes actuales al recién conectado
        participants = await self._get_participants()
        user_ids = [uid for uid in participants.keys() if int(uid) != self.user.id]
        await self.send_json({'type': 'participants', 'users': user_ids})

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            # 2. Eliminar de la "Pizarra Central"
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

            if event_type in ('offer', 'answer', 'ice_candidate'):
                await self._relay_signal(event_type, data)
            elif event_type == 'leave_room':
                await self.close()
            else:
                await self.send_json({'type': 'error', 'detail': f'Tipo desconocido: {event_type}'})
        except json.JSONDecodeError:
            await self.send_json({'type': 'error', 'detail': 'JSON inválido.'})

    # ── Relay de señales WebRTC ──────────────────────────────────────────────
    async def _relay_signal(self, signal_type, data):
        """Reenvía offer/answer/ice_candidate al target o a todos."""
        target_id = data.get('target')
        payload   = {
            'type': signal_type,
            'from': self.user.id,
        }
        if signal_type in ('offer', 'answer'):
            payload['sdp'] = data.get('sdp')
        else:
            payload['candidate'] = data.get('candidate')

        if target_id:
            # Punto a punto: buscar channel_name del target en Redis
            participants = await self._get_participants()
            target_data = participants.get(str(target_id)) # La cache guarda keys como string

            if target_data and 'channel' in target_data:
                await self.channel_layer.send(target_data['channel'], {'type': signal_type, **payload})
            else:
                await self.send_json({'type': 'error', 'detail': 'Destinatario no encontrado o desconectado.'})
        else:
            # Broadcast a todos excepto el emisor
            await self.channel_layer.group_send(self.room_name, payload)

    # ── Handlers del grupo ───────────────────────────────────────────────────
    async def user_joined(self, event):
        if event['user_id'] != self.user.id:
            await self.send_json({'type': 'user_joined', 'user_id': event['user_id'], 'username': event['username']})

    async def user_left(self, event):
        await self.send_json({'type': 'user_left', 'user_id': event['user_id']})

    async def offer(self, event):
        if event.get('from') != self.user.id:
            await self.send_json({'type': 'offer', 'sdp': event.get('sdp'), 'from': event.get('from')})

    async def answer(self, event):
        if event.get('from') != self.user.id:
            await self.send_json({'type': 'answer', 'sdp': event.get('sdp'), 'from': event.get('from')})

    async def ice_candidate(self, event):
        if event.get('from') != self.user.id:
            await self.send_json({'type': 'ice_candidate', 'candidate': event.get('candidate'), 'from': event.get('from')})

    # ── Helpers de Cache (Redis) ─────────────────────────────────────────────
    @sync_to_async
    def _add_participant(self):
        participants = cache.get(self.cache_key, {})
        participants[str(self.user.id)] = {
            'channel': self.channel_name,
            'username': self.user.username
        }
        cache.set(self.cache_key, participants, timeout=7200) # Expira en 2 horas

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

    # ── Helpers DB ───────────────────────────────────────────────────────────
    async def send_json(self, content):
        await self.send(text_data=json.dumps(content, default=str))

    @database_sync_to_async
    def _session_is_available(self):
        from learning.models import LiveSession
        return LiveSession.objects.filter(
            pk=self.session_id, status__in=('scheduled', 'live')
        ).exists()
