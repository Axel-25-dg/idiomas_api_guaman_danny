from django.db import models
from django.conf import settings
from django.utils import timezone
from .course import Lesson


STATUS_CHOICES = [
    ('in_progress', 'En curso'),
    ('completed', 'Completado'),
]


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-completed_at']
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f'{self.user.email} - {self.lesson.title} ({self.status})'


class UserStats(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stats')
    total_xp = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-total_xp']

    def __str__(self):
        return f'Stats de {self.user.email} - XP: {self.total_xp}'

    @property
    def level(self):
        """Nivel calculado: cada 100 XP sube un nivel."""
        return (self.total_xp // 100) + 1

    @property
    def xp_for_next_level(self):
        return self.level * 100

    @property
    def xp_progress_in_level(self):
        """XP acumulado dentro del nivel actual (0–99)."""
        return self.total_xp % 100


class Achievement(models.Model):
    """
    Logro / pin de reconocimiento.
    Se desbloquea automáticamente cuando el usuario alcanza el XP requerido.
    También se puede asociar a eventos específicos (racha, curso, etc.) con trigger_type.
    """
    TRIGGER_XP       = 'xp'
    TRIGGER_STREAK   = 'streak'
    TRIGGER_COURSE   = 'course'
    TRIGGER_MESSAGES = 'messages'
    TRIGGER_MANUAL   = 'manual'

    TRIGGER_CHOICES = [
        (TRIGGER_XP,       'Por XP acumulado'),
        (TRIGGER_STREAK,   'Por racha de días'),
        (TRIGGER_COURSE,   'Por cursos completados'),
        (TRIGGER_MESSAGES, 'Por mensajes enviados'),
        (TRIGGER_MANUAL,   'Manual / admin'),
    ]

    name         = models.CharField(max_length=100)
    description  = models.TextField()
    icon_url     = models.URLField(blank=True, null=True)
    required_xp  = models.PositiveIntegerField(default=0)
    trigger_type = models.CharField(
        max_length=20, choices=TRIGGER_CHOICES, default=TRIGGER_XP, db_index=True
    )
    # Valor umbral para triggers distintos al XP (ej: 7 días de racha)
    required_value = models.PositiveIntegerField(
        default=0,
        help_text='Valor umbral para el trigger (días de racha, cursos, etc.)'
    )
    is_active    = models.BooleanField(default=True, db_index=True)
    created_at   = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['required_xp', 'name']

    def __str__(self):
        return f'{self.name} ({self.required_xp} XP)'


class UserAchievement(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='users')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-unlocked_at']
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f'{self.user.email} desbloqueó {self.achievement.name}'
