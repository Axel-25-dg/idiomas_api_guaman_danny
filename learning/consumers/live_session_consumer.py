"""
LiveSessionConsumer — WebSocket para señalización WebRTC
=========================================================
ws/live-session/<session_id>/

Flujo WebRTC estándar (señalización via WebSocket):
  1. Participante A se conecta  → broadcast 'user_joined'
  2. A envía 'offer'            → se reenvía a B
  3. B responde 'answer'        → se reenvía a A
  4. A y B intercambian 'ice_candidate' entre sí
  5. Conexión P2P establecida (canal de datos/video/audio)

Eventos del cliente → servidor:
  { "type": "offer",          "sdp": {...},      "target": <user_id> }
  { "type": "answer",         "sdp": {...},      "target": <user_id> }
  { "type": "ice_candidate",  "candidate": {...}, "target": <user_id> }
  { "type": "leave_room" }

Eventos del servidor → cliente (broadcast o dirigido):
  { "type": "user_joined",    "user_id": ..., "username": ... }
  { "type": "user_left",      "user_id": ... }
  { "type": "offer",          "sdp": {...},   "from": <user_id> }
  { "type": "answer",         "sdp": {...},   "from": <user_id> }
  { "type": "ice_candidate",  "candidate": {...}, "from": <user_id> }
  { "type": "participants",   "users": [...] }
  { "type": "error",          "detail": "..." }
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Almacenamiento en memoria de participantes activos por sala
# { "session_<id>": { user_id: channel_name, ... } }
_room_participants: dict[str, dict[int, str]] = {}


class LiveSessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user       = self.scope['user']
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_name  = f'session_{self.session_id}'

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        if not await self._session_is_available():
            await self.close(code=4404)
            return

        # Registrar en la sala
        if self.room_name not in _room_participants:
            _room_participants[self.room_name] = {}
        _room_participants[self.room_name][self.user.id] = self.channel_name

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
        participants = [
            {'user_id': uid, 'channel': ch}
            for uid, ch in _room_participants[self.room_name].items()
            if uid != self.user.id
        ]
        await self.send_json({'type': 'participants', 'users': [p['user_id'] for p in participants]})

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            _room_participants.get(self.room_name, {}).pop(self.user.id, None)
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
            # Punto a punto: buscar channel_name del target
            target_channel = _room_participants.get(self.room_name, {}).get(int(target_id))
            if target_channel:
                await self.channel_layer.send(target_channel, {'type': signal_type, **payload})
            else:
                await self.send_json({'type': 'error', 'detail': 'Destinatario no encontrado en la sala.'})
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

    # ── Helpers ──────────────────────────────────────────────────────────────
    async def send_json(self, content):
        await self.send(text_data=json.dumps(content, default=str))

    @database_sync_to_async
    def _session_is_available(self):
        from learning.models import LiveSession
        return LiveSession.objects.filter(
            pk=self.session_id, status__in=('scheduled', 'live')
        ).exists()
