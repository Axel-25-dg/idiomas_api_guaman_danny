"""
ChatConsumer — WebSocket para mensajería en tiempo real
=======================================================
ws/chat/<thread_id>/

Eventos del cliente → servidor:
  { "type": "chat_message",  "body": "Hola!"  }
  { "type": "typing",        "is_typing": true }
  { "type": "read_message",  "message_id": 42  }

Eventos del servidor → cliente:
  { "type": "chat_message",  "message": {...}  }
  { "type": "typing",        "user_id": 1, "is_typing": true }
  { "type": "read_receipt",  "message_id": 42, "reader_id": 2 }
  { "type": "error",         "detail": "..." }
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):

    # ── Conexión ─────────────────────────────────────────────────────────────
    async def connect(self):
        self.user      = self.scope['user']
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_name = f'chat_{self.thread_id}'

        # Rechazar anónimos
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Verificar que el usuario pertenece al hilo
        if not await self._is_participant():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    # ── Desconexión ──────────────────────────────────────────────────────────
    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    # ── Recibir del cliente ──────────────────────────────────────────────────
    async def receive(self, text_data):
        try:
            data      = json.loads(text_data)
            event_type = data.get('type')

            if event_type == 'chat_message':
                await self._handle_chat_message(data)
            elif event_type == 'typing':
                await self._handle_typing(data)
            elif event_type == 'read_message':
                await self._handle_read_message(data)
            else:
                await self.send_json({'type': 'error', 'detail': f'Tipo de evento desconocido: {event_type}'})
        except json.JSONDecodeError:
            await self.send_json({'type': 'error', 'detail': 'JSON inválido.'})
        except Exception as exc:
            await self.send_json({'type': 'error', 'detail': str(exc)})

    # ── Handlers de eventos entrantes ────────────────────────────────────────
    async def _handle_chat_message(self, data):
        body = (data.get('body') or '').strip()
        if not body:
            await self.send_json({'type': 'error', 'detail': 'El mensaje no puede estar vacío.'})
            return

        msg = await self._save_message(body)
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':    'chat_message',
                'message': {
                    'id':         msg.id,
                    'thread':     msg.thread_id,
                    'sender_id':  self.user.id,
                    'sender':     self.user.email,
                    'body':       msg.body,
                    'is_read':    False,
                    'created_at': msg.created_at.isoformat(),
                },
            },
        )

        import asyncio
        if await self._is_ai_thread():
            asyncio.create_task(self._process_ai_message(body, msg.thread_id))

    async def _handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':      'typing',
                'user_id':   self.user.id,
                'username':  self.user.username,
                'is_typing': bool(data.get('is_typing', False)),
            },
        )

    async def _handle_read_message(self, data):
        message_id = data.get('message_id')
        if not message_id:
            return
        success = await self._mark_message_read(message_id)
        if success:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type':       'read_receipt',
                    'message_id': message_id,
                    'reader_id':  self.user.id,
                },
            )

    # ── Handlers de eventos del grupo (salida al cliente) ────────────────────
    async def chat_message(self, event):
        await self.send_json({'type': 'chat_message', 'message': event['message']})

    async def typing(self, event):
        # No enviar al propio emisor
        if event['user_id'] != self.user.id:
            await self.send_json({
                'type':      'typing',
                'user_id':   event['user_id'],
                'username':  event['username'],
                'is_typing': event['is_typing'],
            })

    async def read_receipt(self, event):
        await self.send_json({
            'type':       'read_receipt',
            'message_id': event['message_id'],
            'reader_id':  event['reader_id'],
        })

    # ── Helpers ──────────────────────────────────────────────────────────────
    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))

    @database_sync_to_async
    def _is_participant(self):
        from learning.models import MessageThread
        try:
            thread = MessageThread.objects.get(pk=self.thread_id, is_active=True)
            return thread.participants.filter(pk=self.user.pk).exists()
        except MessageThread.DoesNotExist:
            return False

    @database_sync_to_async
    def _save_message(self, body):
        from learning.models import Message, MessageThread
        thread = MessageThread.objects.get(pk=self.thread_id)
        msg    = Message.objects.create(thread=thread, sender=self.user, body=body)
        thread.save(update_fields=['updated_at'])
        return msg

    @database_sync_to_async
    def _mark_message_read(self, message_id):
        from learning.models import Message
        updated = Message.objects.filter(
            pk=message_id,
            thread_id=self.thread_id,
            is_read=False,
        ).exclude(sender=self.user).update(is_read=True, read_at=timezone.now())
        return updated > 0

    async def _process_ai_message(self, user_text, thread_id):
        # 1. Indicador de "Escribiendo..."
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':      'typing',
                'user_id':   0, # ID del bot simulado
                'username':  'Tutor IA',
                'is_typing': True,
            },
        )
        
        # 2. Consultar al servicio de IA
        from learning.services.ai_service import get_ai_response
        ai_reply_text = await get_ai_response(user_text)
        
        # 3. Guardar el mensaje del bot en la BD
        ai_msg = await self._save_ai_message(ai_reply_text, thread_id)
        
        # 4. Quitar el "Escribiendo..." y enviar el mensaje
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':      'typing',
                'user_id':   0,
                'username':  'Tutor IA',
                'is_typing': False,
            },
        )
        
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':    'chat_message',
                'message': {
                    'id':         ai_msg.id,
                    'thread':     ai_msg.thread_id,
                    'sender_id':  ai_msg.sender.id,
                    'sender':     ai_msg.sender.email,
                    'body':       ai_msg.body,
                    'is_read':    False,
                    'created_at': ai_msg.created_at.isoformat(),
                },
            },
        )

    @database_sync_to_async
    def _is_ai_thread(self):
        from learning.models import MessageThread
        try:
            thread = MessageThread.objects.get(pk=self.thread_id)
            return thread.participants.count() == 1 or 'IA' in (thread.subject or '').upper()
        except Exception:
            return False

    @database_sync_to_async
    def _save_ai_message(self, body, thread_id):
        from learning.models import Message, MessageThread
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        ai_user, _ = User.objects.get_or_create(
            username='tutor_ia',
            defaults={
                'email': 'ia@jumpup.com',
                'first_name': 'Tutor',
                'last_name': 'IA',
                'is_active': True
            }
        )
        
        thread = MessageThread.objects.get(pk=thread_id)
        if not thread.participants.filter(id=ai_user.id).exists():
            thread.participants.add(ai_user)

        msg = Message.objects.create(thread=thread, sender=ai_user, body=body)
        thread.save(update_fields=['updated_at'])
        return msg
