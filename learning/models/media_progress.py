"""
Módulo de Progreso Multimedia
==============================
MediaProgress → registra hasta qué punto vio el estudiante un video/audio
"""
from django.db import models
from django.conf import settings
from .course import Lesson


class MediaProgress(models.Model):
    """
    Guarda el progreso de reproducción de un contenido multimedia.
    Permite reanudar desde donde se dejó.
    """
    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='media_progress')
    lesson         = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='media_progress')
    position_sec   = models.PositiveIntegerField(default=0, help_text='Posición en segundos')
    duration_sec   = models.PositiveIntegerField(default=0, help_text='Duración total en segundos')
    completed      = models.BooleanField(default=False)
    last_watched   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'lesson']
        ordering = ['-last_watched']

    @property
    def percentage(self):
        if self.duration_sec > 0:
            return round((self.position_sec / self.duration_sec) * 100, 1)
        return 0.0

    def __str__(self):
        return f'{self.user.email} — {self.lesson.title} ({self.percentage}%)'
