"""
Utilidad central para crear notificaciones y enviarlas por WebSocket.
======================================================================
Usar desde cualquier view, signal o tarea Celery:

  from learning.utils.notify import push_notification

  push_notification(
      user         = request.user,
      title        = 'Nuevo mensaje',
      message      = 'Danny te envió un mensaje.',
      notif_type   = 'message',
  )
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def push_notification(user, title: str, message: str, notif_type: str = 'system') -> None:
    """
    1. Persiste la notificación en la BD.
    2. La empuja en tiempo real al WebSocket del usuario (si está conectado).

    Parámetros:
      user       — instancia de User
      title      — título corto
      message    — texto completo
      notif_type — uno de NotificationType: system, course, payment,
                   certificate, subscription, message, forum, live_session
    """
    from learning.models import Notification

    # Guardar en BD
    notif = Notification.objects.create(
        user    = user,
        title   = title,
        message = message,
        type    = notif_type,
    )

    # Enviar por WebSocket (best-effort: si Redis no está, no falla el request)
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user.id}',
            {
                'type': 'new_notification',
                'notification': {
                    'id':         notif.id,
                    'uuid':       str(notif.uuid),
                    'title':      notif.title,
                    'message':    notif.message,
                    'type':       notif.type,
                    'is_read':    False,
                    'created_at': notif.created_at.isoformat(),
                },
            },
        )
    except Exception:
        # Redis no disponible — la notificación ya está en BD, no bloquear
        pass
