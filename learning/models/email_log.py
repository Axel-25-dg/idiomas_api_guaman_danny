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


class BroadcastEmail(TimestampedModel):
    AUDIENCE_CHOICES = [
        ('all', 'Todos los usuarios'),
        ('students', 'Todos los estudiantes'),
        ('teachers', 'Todos los profesores'),
        ('course', 'Estudiantes de un curso específico'),
    ]

    subject = models.CharField(max_length=255, verbose_name="Asunto")
    message = models.TextField(verbose_name="Mensaje")
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all', verbose_name="Audiencia")
    target_course = models.ForeignKey(
        'learning.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Curso objetivo (si aplica)"
    )
    action_url = models.URLField(blank=True, null=True, verbose_name="URL del botón (Opcional)")
    action_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="Texto del botón")
    
    sent_count = models.PositiveIntegerField(default=0, verbose_name="Correos enviados")
    is_sent = models.BooleanField(default=False, verbose_name="¿Enviado?")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de envío")

    class Meta:
        verbose_name = "Envío masivo"
        verbose_name_plural = "Envíos masivos"
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} ({self.get_audience_display()})'
