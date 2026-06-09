import uuid
from django.db import models
from django.conf import settings
from .course import DIFFICULTY_CHOICES


def generate_certificate_code():
    """Genera un código de certificado único. Ej: 'CERT-A1-3F9K2T8A'"""
    return f'CERT-{uuid.uuid4().hex[:8].upper()}'


CERTIFICATE_STATUS_CHOICES = [
    ('pending',  'Pendiente de revisión'),
    ('issued',   'Emitido'),
    ('revoked',  'Revocado'),
]


class Certificate(models.Model):
    """
    Certificado de nivel MCER emitido a un estudiante al completar un curso.
    Niveles válidos: A1, A2, B1, B2, C1, C2 (reutiliza DIFFICULTY_CHOICES de Course).

    Flujo:
      1. El sistema o el profesor crea el certificado con status='pending'.
      2. El admin/profesor lo aprueba → status='issued'.
      3. Se genera un código único para verificación externa.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    student          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    issued_by        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificates_issued',
        limit_choices_to={'is_staff': True},
    )
    level            = models.CharField(
        max_length=2,
        choices=DIFFICULTY_CHOICES,
        help_text='Nivel MCER: A1, A2, B1, B2, C1, C2',
    )
    title            = models.CharField(
        max_length=200,
        help_text='Ej: "Certificado de Inglés A1 — JumpUp UTE"',
    )
    description      = models.TextField(blank=True)
    certificate_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_certificate_code,
        editable=False,
        help_text='Código único de verificación del certificado',
    )
    certificate_file = models.ForeignKey(
        'MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificates',
    )
    status           = models.CharField(
        max_length=10,
        choices=CERTIFICATE_STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    issued_at        = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at       = models.DateTimeField(auto_now=True)
    deleted_at       = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering        = ['-created_at']
        unique_together = ['student', 'level']  # un certificado por nivel por estudiante
        indexes = [models.Index(fields=['level']), models.Index(fields=['status'])]

    def __str__(self):
        return f'{self.certificate_code} — {self.student.email} ({self.level})'
