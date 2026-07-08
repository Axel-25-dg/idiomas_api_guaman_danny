from unittest.mock import MagicMock, patch

from asgiref.sync import async_to_sync
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from learning.middleware import JwtAuthMiddleware
from learning.models import User, Notification
from learning.utils.notify import push_notification


class JwtAuthMiddlewareTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='wsuser',
            email='wsuser@example.com',
            password='TestPass123!',
        )

    def test_authenticates_user_from_authorization_header(self):
        token = str(RefreshToken.for_user(self.user).access_token)
        captured = {}

        async def app(scope, receive, send):
            captured['user'] = scope['user']

        middleware = JwtAuthMiddleware(app)
        scope = {
            'type': 'websocket',
            'query_string': b'',
            'headers': [(b'authorization', f'Bearer {token}'.encode('utf-8'))],
        }

        async_to_sync(middleware)(scope, lambda: None, lambda message: None)

        self.assertEqual(captured['user'].pk, self.user.pk)


class NotificationUtilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='notifyuser',
            email='notifyuser@example.com',
            password='TestPass123!',
        )

    def test_push_notification_persists_notification(self):
        with patch('learning.utils.notify.get_channel_layer') as get_channel_layer:
            mocked_layer = MagicMock()
            get_channel_layer.return_value = mocked_layer
            push_notification(self.user, 'Hola', 'Mensaje de prueba', 'message')

        notification = Notification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, 'Hola')
        self.assertFalse(notification.is_read)
