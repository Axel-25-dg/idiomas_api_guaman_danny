"""
Signals — Lógica automática de gamificación
=============================================

1. on_progress_saved:
   - Cuando un progreso se marca como 'completed':
     - Suma xp_reward al UserStats.
     - Actualiza rachas basadas en días reales de actividad.

2. on_stats_updated:
   - Cuando XP cambia, verifica logros y desbloquea automáticamente.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta


@receiver(post_save, sender='learning.UserProgress')
def on_progress_saved(sender, instance, created, **kwargs):
    """
    Cuando un progreso se marca como 'completed':
    1. Marca completed_at si no estaba marcado.
    2. Suma xp_reward de la lección al UserStats.
    3. Actualiza rachas basadas en la fecha real.
    """
    if instance.status != 'completed':
        return

    # Solo procesar la primera vez que se completa (completed_at == None)
    if instance.completed_at is not None:
        return

    from learning.models import UserStats

    now = timezone.now()

    # Marcar completed_at sin volver a disparar el signal
    sender.objects.filter(pk=instance.pk).update(completed_at=now)

    user = instance.user
    xp_reward = instance.lesson.xp_reward

    # Obtener o crear stats
    stats, created_stats = UserStats.objects.get_or_create(user=user)

    # ── Sumar XP ──────────────────────────────────────────────────────────
    stats.total_xp += xp_reward

    # ── Actualizar rachas (basado en días) ────────────────────────────────
    today = now.date()

    # Buscar la última lección completada ANTES de esta
    last_completion = sender.objects.filter(
        user=user,
        status='completed',
        completed_at__isnull=False,
    ).exclude(pk=instance.pk).order_by('-completed_at').first()

    if last_completion and last_completion.completed_at:
        last_date = last_completion.completed_at.date()
        diff = (today - last_date).days

        if diff == 1:
            # Día consecutivo → incrementar racha
            stats.current_streak += 1
        elif diff == 0:
            # Mismo día → no cambiar racha (ya contó)
            pass
        else:
            # Se rompió la racha → reiniciar a 1
            stats.current_streak = 1
    else:
        # Primera lección completada del usuario
        stats.current_streak = 1

    # Actualizar mejor racha
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
    unlocked_ids = set(
        UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
    )

    new_achievements = Achievement.objects.filter(
        required_xp__lte=current_xp
    ).exclude(id__in=unlocked_ids)

    # Crear UserAchievement para cada logro nuevo
    new_records = [
        UserAchievement(user=user, achievement=achievement)
        for achievement in new_achievements
    ]

    if new_records:
        UserAchievement.objects.bulk_create(new_records, ignore_conflicts=True)
