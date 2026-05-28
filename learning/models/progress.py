from django.db import models
from django.conf import settings
from .course import Lesson


STATUS_CHOICES = [
    ('in_progress', 'En curso'),
    ('completed', 'Completado'),
]

PAYMENT_STATUS_CHOICES = [
    ('approved', 'Aprobado'),
    ('rejected', 'Rechazado'),
    ('pending', 'Pendiente'),
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

    class Meta:
        ordering = ['-total_xp']

    def __str__(self):
        return f'Stats de {self.user.email} - XP: {self.total_xp}'


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_url = models.URLField(blank=True, null=True)
    required_xp = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['required_xp']

    def __str__(self):
        return f'{self.name} ({self.required_xp} XP)'


class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='users')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-unlocked_at']
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f'{self.user.email} desbloqueó {self.achievement.name}'
