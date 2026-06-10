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


@receiver(post_save, sender='learning.User')
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un UserProfile cada vez que se registra un nuevo usuario.
    """
    if created:
        from learning.models import UserProfile
        UserProfile.objects.get_or_create(user=instance)


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

    # Obtener logros que el usuario aún no tiene
    achieved_ids = UserAchievement.objects.filter(user=instance.user).values_list('achievement_id', flat=True)
    available = Achievement.objects.filter(is_active=True).exclude(id__in=achieved_ids)

    for achievement in available:
        if instance.total_xp >= achievement.required_xp:
            UserAchievement.objects.create(
                user=instance.user,
                achievement=achievement
            )


@receiver(post_save, sender='learning.Lesson')
def notify_new_lesson(sender, instance, created, **kwargs):
    """
    Notifica a todos los estudiantes inscritos en un curso cuando se añade una nueva lección.
    """
    if created:
        from learning.models import UserProgress, User
        from learning.services.email_service import send_custom_email
        from django.conf import settings
        
        course = instance.module.course
        
        # Obtener IDs de estudiantes que ya tienen progreso en este curso
        student_ids = UserProgress.objects.filter(
            lesson__module__course=course
        ).values_list('user_id', flat=True).distinct()
        
        students = User.objects.filter(id__in=student_ids, is_active=True)
        
        subject = f"¡Nueva lección en {course.title}!"
        message = f"Se ha añadido una nueva lección: '{instance.title}'. ¡Ven a verla y sigue aprendiendo!"
        action_url = f"{settings.FRONTEND_URL}/courses/{course.id}"
        
        for student in students:
            try:
                send_custom_email(student, subject, message, action_url, "Ver lección")
            except Exception:
                pass
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
