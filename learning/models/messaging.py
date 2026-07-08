"""
Módulo de Mensajería
====================
MessageThread  → hilo de conversación entre dos usuarios
Message        → mensaje individual dentro de un hilo
MessageAttachment → archivos adjuntos de un mensaje
"""
from django.db import models
from django.conf import settings


class MessageThread(models.Model):
    """Hilo de conversación (alumno ↔ profesor)."""
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='message_threads',
        blank=False,
    )
    subject      = models.CharField(max_length=200, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    is_active    = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'Thread #{self.pk} — {self.subject or "Sin asunto"}'


class Message(models.Model):
    """Mensaje dentro de un hilo."""
    thread     = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    body       = models.TextField()
    is_read    = models.BooleanField(default=False)
    read_at    = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Msg de {self.sender.email} en Thread #{self.thread_id}'


class MessageAttachment(models.Model):
    """Archivo adjunto de un mensaje."""
    ATTACHMENT_TYPE_CHOICES = [
        ('image',    'Imagen'),
        ('audio',    'Audio'),
        ('document', 'Documento'),
        ('other',    'Otro'),
    ]
    message         = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file_url        = models.URLField(help_text='URL del archivo en almacenamiento externo')
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPE_CHOICES, default='document')
    filename        = models.CharField(max_length=255, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.attachment_type}: {self.filename}'
