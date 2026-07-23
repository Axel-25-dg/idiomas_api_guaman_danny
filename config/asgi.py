"""
ASGI config — JumpUp UTE
========================
HTTP  → Django WSGI clásico
WS    → Django Channels + Redis Channel Layer

Ejecutar en producción:
  daphne config.asgi:application --bind 0.0.0.0 --port 8001
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from learning.middleware import JwtAuthMiddleware
from learning.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Inicializar Django antes de importar modelos/consumers
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # HTTP → handler normal de Django
    'http': django_asgi_app,

    # WebSocket → autenticación JWT + rutas
    'websocket': JwtAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
