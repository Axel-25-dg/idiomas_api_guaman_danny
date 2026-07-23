"""
JwtAuthMiddleware — autentica conexiones WebSocket con el mismo token JWT
que usa la API REST.

Uso:
  El cliente debe enviar el token en el query string:
    ws://host/ws/chat/1/?token=<access_token>

  O en la subpropuesta de cookie (configuración alternativa).
"""
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user_from_token(token_key: str):
    """Valida el JWT y devuelve el User o AnonymousUser."""
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError
        from learning.models import User

        token = AccessToken(token_key)
        user  = User.objects.get(pk=token['user_id'])
        return user
    except Exception:
        from django.contrib.auth.models import AnonymousUser
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    """Middleware ASGI que inyecta el usuario autenticado en el scope."""

    async def __call__(self, scope, receive, send):
        token_key = None

        # 1) Query string: ?token=<jwt>
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token_list = params.get('token', [None])
        token_key = token_list[0] if token_list else None

        # 2) Header Authorization: Bearer <jwt>
        if not token_key:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization')
            if auth_header:
                auth_value = auth_header.decode('utf-8')
                if auth_value.startswith('Bearer '):
                    token_key = auth_value.split(' ', 1)[1].strip()

        if token_key:
            scope['user'] = await get_user_from_token(token_key)
        else:
            from django.contrib.auth.models import AnonymousUser
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
