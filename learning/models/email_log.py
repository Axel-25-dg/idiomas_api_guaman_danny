import uuid
from django.db import models
from django.conf import settings

from .base import TimestampedModel


EMAIL_STATUS_CHOICES = [
    ('pending', 'Pendiente'),
    ('sent', 'Enviado'),
    ('failed', 'Fallido'),
]


class EmailLog(TimestampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    recipient = models.EmailField(db_index=True)
    subject = models.CharField(max_length=255)
    template_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=EMAIL_STATUS_CHOICES, default='pending', db_index=True)
    response = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.recipient} — {self.subject} ({self.status})'
