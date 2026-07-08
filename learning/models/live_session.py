"""
Módulo de Videotutoría / Sesiones en Vivo
==========================================
LiveSession     → sesión de videotutoría creada por un profesor
LiveParticipant → participante inscrito en una sesión
"""
from django.db import models
from django.conf import settings
from .course import Course


SESSION_STATUS_CHOICES = [
    ('scheduled', 'Programada'),
    ('live',      'En vivo'),
    ('ended',     'Finalizada'),
    ('cancelled', 'Cancelada'),
]


class LiveSession(models.Model):
    teacher      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='live_sessions_taught',
        limit_choices_to={'is_staff': True},
    )
    course       = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='live_sessions')
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    duration_min = models.PositiveIntegerField(default=60, help_text='Duración estimada en minutos')
    meeting_url  = models.URLField(blank=True, help_text='URL de Zoom/Meet/WebRTC')
    status       = models.CharField(max_length=10, choices=SESSION_STATUS_CHOICES, default='scheduled')
    max_students = models.PositiveIntegerField(default=30)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'{self.title} — {self.get_status_display()}'


class LiveParticipant(models.Model):
    session    = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='participants')
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_participations')
    joined_at  = models.DateTimeField(auto_now_add=True)
    left_at    = models.DateTimeField(null=True, blank=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        unique_together = ['session', 'student']
        ordering = ['joined_at']

    def __str__(self):
        return f'{self.student.email} → {self.session.title}'
