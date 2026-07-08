"""
NotificationConsumer — WebSocket para notificaciones en tiempo real
====================================================================
ws/notifications/

El servidor envía al cliente cuando ocurre un evento:
  { "type": "new_notification",    "notification": {...} }
  { "type": "unread_count",        "count": 5 }
  { "type": "notification_deleted","id": 42 }

El cliente puede enviar:
  { "type": "mark_read",    "notification_id": 42 }
  { "type": "mark_all_read"                        }

Para enviar desde el backend (views/signals):
  from channels.layers import get_channel_layer
  from asgiref.sync import async_to_sync

  channel_layer = get_channel_layer()
  async_to_sync(channel_layer.group_send)(
      f'notifications_{user_id}',
      {
          'type':         'new_notification',
          'notification': { 'id': ..., 'title': ..., ... },
      }
  )
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Enviar contador de no leídas al conectarse
        count = await self._unread_count()
        await self.send_json({'type': 'unread_count', 'count': count})

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data       = json.loads(text_data)
            event_type = data.get('type')

            if event_type == 'mark_read':
                notif_id = data.get('notification_id')
                if notif_id:
                    await self._mark_read(notif_id)
                    count = await self._unread_count()
                    await self.send_json({'type': 'unread_count', 'count': count})

            elif event_type == 'mark_all_read':
                await self._mark_all_read()
                await self.send_json({'type': 'unread_count', 'count': 0})

        except json.JSONDecodeError:
            await self.send_json({'type': 'error', 'detail': 'JSON inválido.'})

    # ── Handlers del grupo (enviados por el backend) ─────────────────────────
    async def new_notification(self, event):
        """Nuevo evento de notificación enviado por el backend."""
        await self.send_json({
            'type':         'new_notification',
            'notification': event.get('notification', {}),
        })
        count = await self._unread_count()
        await self.send_json({'type': 'unread_count', 'count': count})

    async def notification_deleted(self, event):
        await self.send_json({'type': 'notification_deleted', 'id': event.get('id')})

    # ── Helpers ──────────────────────────────────────────────────────────────
    async def send_json(self, content):
        await self.send(text_data=json.dumps(content, default=str))

    @database_sync_to_async
    def _unread_count(self):
        from learning.models import Notification
        return Notification.objects.filter(user=self.user, is_read=False).count()

    @database_sync_to_async
    def _mark_read(self, notif_id):
        from learning.models import Notification
        Notification.objects.filter(pk=notif_id, user=self.user).update(is_read=True)

    @database_sync_to_async
    def _mark_all_read(self):
        from learning.models import Notification
        Notification.objects.filter(user=self.user, is_read=False).update(is_read=True)
