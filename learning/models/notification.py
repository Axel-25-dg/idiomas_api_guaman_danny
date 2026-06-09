import uuid
from django.db import models
from django.conf import settings

from .base import TimestampedModel


class NotificationType(models.TextChoices):
    SYSTEM = 'system', 'Sistema'
    COURSE = 'course', 'Curso'
    PAYMENT = 'payment', 'Pago'
    CERTIFICATE = 'certificate', 'Certificado'
    SUBSCRIPTION = 'subscription', 'Suscripción'


class Notification(TimestampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read'])]

    def __str__(self):
        return f'{self.user.email} — {self.title}'
