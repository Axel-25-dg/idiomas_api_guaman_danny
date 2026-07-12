"""
GamificationService — Lógica centralizada de gamificación
===========================================================
Funciones utilitarias para sumar XP manualmente, verificar logros
y actualizar rachas desde cualquier parte del backend.

Uso básico:
    from learning.services.gamification_service import (
        award_xp, check_and_unlock_achievements, update_streak
    )
    award_xp(user, xp=50, reason='ejercicio_completado')
"""

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def award_xp(user, xp: int, reason: str = '') -> dict:
    """
    Suma XP al usuario directamente (fuera del flujo de lecciones).
    Útil para premiar: participación en foro, racha, etc.

    Retorna dict con el estado actualizado de stats.
    """
    from learning.models import UserStats

    if xp <= 0:
        return {}

    stats, _ = UserStats.objects.get_or_create(user=user)
    stats.total_xp += xp
    stats.save(update_fields=['total_xp'])

    logger.info('award_xp: +%d XP a %s (motivo: %s). Total: %d', xp, user.email, reason, stats.total_xp)

    return {
        'total_xp':             stats.total_xp,
        'level':                stats.level,
        'xp_progress_in_level': stats.xp_progress_in_level,
    }


def update_streak(user) -> dict:
    """
    Recalcula la racha del usuario basándose en la fecha de hoy.
    Llamar una vez al día por usuario activo (ej: al hacer login o completar ejercicio).
    """
    from learning.models import UserStats

    stats, _ = UserStats.objects.get_or_create(user=user)
    today    = timezone.now().date()

    if stats.last_activity_date is None:
        stats.current_streak = 1
    else:
        diff = (today - stats.last_activity_date).days
        if diff == 0:
            pass  # ya se contó hoy
        elif diff == 1:
            stats.current_streak += 1
        else:
            stats.current_streak = 1

    if stats.current_streak > stats.longest_streak:
        stats.longest_streak = stats.current_streak

    stats.last_activity_date = today
    stats.save(update_fields=['current_streak', 'longest_streak', 'last_activity_date'])

    logger.info('update_streak: %s → streak=%d', user.email, stats.current_streak)
    return {
        'current_streak': stats.current_streak,
        'longest_streak': stats.longest_streak,
    }


def check_and_unlock_achievements(user) -> list:
    """
    Verifica todos los logros activos y desbloquea los que el usuario ya cumple.
    Retorna lista de logros recién desbloqueados.
    Idempotente: se puede llamar múltiples veces sin duplicar.
    """
    from learning.models import UserStats, Achievement, UserAchievement
    from learning.signals import push_ws_notification

    stats, _ = UserStats.objects.get_or_create(user=user)

    owned_ids = set(
        UserAchievement.objects.filter(user=user)
        .values_list('achievement_id', flat=True)
    )

    newly_unlocked = []

    for ach in Achievement.objects.filter(is_active=True).exclude(id__in=owned_ids):
        earned = False

        if ach.trigger_type == Achievement.TRIGGER_XP:
            earned = stats.total_xp >= ach.required_xp

        elif ach.trigger_type == Achievement.TRIGGER_STREAK:
            threshold = ach.required_value or ach.required_xp
            earned = stats.current_streak >= threshold

        elif ach.trigger_type == Achievement.TRIGGER_COURSE:
            from learning.models import UserProgress, Course, Lesson
            threshold = ach.required_value or 1
            completed = 0
            for course in Course.objects.filter(is_active=True):
                total = Lesson.objects.filter(module__course=course, is_active=True).count()
                if total == 0:
                    continue
                done = UserProgress.objects.filter(
                    user=user, status='completed', lesson__module__course=course
                ).count()
                if done >= total:
                    completed += 1
            earned = completed >= threshold

        if earned:
            ua, created = UserAchievement.objects.get_or_create(user=user, achievement=ach)
            if created:
                newly_unlocked.append(ach)
                push_ws_notification(
                    user_id=user.id,
                    title=f'🏅 Logro desbloqueado: {ach.name}',
                    message=ach.description,
                    notif_type='system',
                )

    if newly_unlocked:
        logger.info('%d logros desbloqueados para %s', len(newly_unlocked), user.email)

    return newly_unlocked


def get_user_level_info(user) -> dict:
    """
    Retorna toda la información de nivel/XP del usuario.
    """
    from learning.models import UserStats
    stats, _ = UserStats.objects.get_or_create(user=user)
    return {
        'total_xp':             stats.total_xp,
        'level':                stats.level,
        'xp_for_next_level':    stats.xp_for_next_level,
        'xp_progress_in_level': stats.xp_progress_in_level,
        'current_streak':       stats.current_streak,
        'longest_streak':       stats.longest_streak,
        'last_activity_date':   stats.last_activity_date,
    }


def has_active_subscription(user) -> bool:
    """Retorna True para simular suscripción activa bajo modelo de venta directa."""
    return True


def get_max_languages(user) -> int:
    """
    Devuelve cuántos idiomas puede aprender el usuario.
    0 = ilimitado (venta directa).
    """
    return 0
