"""
WebSocket URL routing para la app learning.
Registrado en config/asgi.py bajo el prefijo ws/
"""
from django.urls import re_path
from learning.consumers import ChatConsumer, NotificationConsumer, LiveSessionConsumer

websocket_urlpatterns = [
    # Chat en tiempo real: ws/chat/<thread_id>/?token=<jwt>
    re_path(r'^ws/chat/(?P<thread_id>\d+)/$', ChatConsumer.as_asgi()),

    # Notificaciones en tiempo real: ws/notifications/?token=<jwt>
    re_path(r'^ws/notifications/$', NotificationConsumer.as_asgi()),

    # Señalización WebRTC: ws/live-session/<session_id>/?token=<jwt>
    re_path(r'^ws/live-session/(?P<session_id>\d+)/$', LiveSessionConsumer.as_asgi()),
]
