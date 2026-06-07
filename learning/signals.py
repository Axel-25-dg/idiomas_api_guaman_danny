"""
Signals — Lógica automática de gamificación
=============================================

Cuando UserStats se actualiza (XP sube), se verifican todos los logros
disponibles y se desbloquean automáticamente los que el usuario ya cumple.

También cuando UserProgress se crea/actualiza como 'completed',
se suma el XP de la lección al UserStats del usuario.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender='learning.UserProgress')
def on_progress_saved(sender, instance, created, **kwargs):
    """
    Cuando un progreso se marca como 'completed':
    1. Suma el xp_reward de la lección al UserStats del usuario.
    2. Actualiza current_streak (simplificado: +1 si completó hoy).
    """
    if instance.status != 'completed':
        return

    from learning.models import UserStats

    user = instance.user
    xp_reward = instance.lesson.xp_reward

    # Obtener o crear stats
    stats, _ = UserStats.objects.get_or_create(user=user)

    # Solo sumar XP si es la primera vez que se completa (created o recién cambió a completed)
    # Para evitar doble suma, usamos un truco: si completed_at es None, lo marcamos
    if instance.completed_at is None:
        instance.completed_at = timezone.now()
        # Guardar sin volver a disparar el signal (update_fields evita recursión)
        sender.objects.filter(pk=instance.pk).update(completed_at=instance.completed_at)

        # Sumar XP
        stats.total_xp += xp_reward
        stats.current_streak += 1
        if stats.current_streak > stats.longest_streak:
            stats.longest_streak = stats.current_streak
        stats.save(update_fields=['total_xp', 'current_streak', 'longest_streak'])


@receiver(post_save, sender='learning.UserStats')
def on_stats_updated(sender, instance, **kwargs):
    """
    Cuando el XP del usuario cambia, verifica todos los logros disponibles
    y desbloquea automáticamente los que ya cumple por XP.
    """
    from learning.models import Achievement, UserAchievement

    user = instance.user
    current_xp = instance.total_xp

    # Logros que el usuario AÚN NO tiene y cuyo required_xp <= current_xp
    unlocked_ids = UserAchievement.objects.filter(
        user=user
    ).values_list('achievement_id', flat=True)

    new_achievements = Achievement.objects.filter(
        required_xp__lte=current_xp
    ).exclude(
        id__in=unlocked_ids
    )

    # Crear UserAchievement para cada logro desbloqueado
    new_records = [
        UserAchievement(user=user, achievement=achievement)
        for achievement in new_achievements
    ]

    if new_records:
        UserAchievement.objects.bulk_create(new_records, ignore_conflicts=True)
