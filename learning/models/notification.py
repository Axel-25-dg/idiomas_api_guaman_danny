import uuid
from django.db import models
from django.conf import settings

from .base import TimestampedModel


class NotificationType(models.TextChoices):
    SYSTEM       = 'system',       'Sistema'
    COURSE       = 'course',       'Curso'
    PAYMENT      = 'payment',      'Pago'
    CERTIFICATE  = 'certificate',  'Certificado'
    SUBSCRIPTION = 'subscription', 'Suscripción'
    MESSAGE      = 'message',      'Mensaje nuevo'
    FORUM        = 'forum',        'Foro'
    LIVE_SESSION = 'live_session', 'Sesión en vivo'


class Announcement(models.Model):
    """Anuncio global visible para todos los usuarios."""
    author     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements'
    )
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    start_date = models.DateTimeField()
    end_date   = models.DateTimeField()
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class Notification(TimestampedModel):
    """
    Notificación individual para un usuario.
    Fuente única de verdad — consolida notification.py y notifications.py.
    """
    uuid    = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title   = models.CharField(max_length=200)
    message = models.TextField()
    type    = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        db_index=True,
    )
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['user', 'is_read'])]

    def __str__(self):
        return f'{self.user.email} — {self.title}'


class UserNotificationPreference(models.Model):
    """Preferencias de notificación por canal para cada usuario."""
    user                = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    email_notifications = models.BooleanField(default=True)
    app_notifications   = models.BooleanField(default=True)
    sms_notifications   = models.BooleanField(default=False)

    def __str__(self):
        return f'Preferencias de {self.user.email}'
