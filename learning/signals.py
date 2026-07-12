"""
Signals — Lógica automática de gamificación y ventas directas
=============================================================

Señales registradas:
  1. create_user_profile       → Crea UserProfile y UserStats al registrar un usuario.
  2. on_progress_saved         → Al completar una lección: suma XP + actualiza racha.
  3. on_stats_updated          → Al cambiar XP: desbloquea logros automáticamente.
  4. (ELIMINADO)               → Suscripciones eliminadas. Ahora se usa venta directa (Orden).
  5. push_ws_notification      → Utilidad interna para guardar+enviar notificación por WebSocket.
  6. notify_achievement_unlock → Al desbloquear un logro: envía notificación en tiempo real.
  7. notify_new_lesson         → Al crear una lección: notifica a estudiantes del curso.
  8. on_order_compra_approved  → Al confirmar una Orden de compra: notifica al profesor.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta, date
import logging

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# UTILIDAD INTERNA
# ──────────────────────────────────────────────────────────────────────────────

def push_ws_notification(user_id: int, title: str, message: str, notif_type: str = 'system') -> None:
    """
    Guarda una Notification en BD y la envía por WebSocket al grupo del usuario.
    Se puede llamar desde cualquier parte del backend:

        from learning.signals import push_ws_notification
        push_ws_notification(user.id, 'Título', 'Cuerpo', 'achievement')
    """
    try:
        from learning.models import Notification
        notif = Notification.objects.create(
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
        )

        # Enviar en tiempo real si Channels + Redis están disponibles
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            if channel_layer is not None:
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{user_id}',
                    {
                        'type': 'new_notification',
                        'notification': {
                            'id':         notif.id,
                            'title':      notif.title,
                            'message':    notif.message,
                            'type':       notif.type,
                            'is_read':    False,
                            'created_at': str(notif.created_at),
                        },
                    }
                )
        except Exception as ws_err:
            logger.warning('WebSocket push falló (canal no disponible): %s', ws_err)

    except Exception as err:
        logger.error('push_ws_notification error: %s', err)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Crear UserProfile + UserStats al registrar un usuario nuevo
# ──────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender='learning.User')
def create_user_profile(sender, instance, created, **kwargs):
    """Crea UserProfile y UserStats automáticamente para cada usuario nuevo."""
    if created:
        from learning.models import UserProfile, UserStats
        UserProfile.objects.get_or_create(user=instance)
        UserStats.objects.get_or_create(user=instance)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Al guardar progreso: sumar XP y actualizar racha
# ──────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender='learning.UserProgress')
def on_progress_saved(sender, instance, created, **kwargs):
    """
    Se dispara cada vez que se guarda un UserProgress.
    Solo actúa cuando status == 'completed' Y completed_at es None
    (primera vez que se completa la lección).
    """
    if instance.status != 'completed':
        return

    # Evitar procesar dos veces la misma lección
    if instance.completed_at is not None:
        return

    from learning.models import UserStats

    now  = timezone.now()
    user = instance.user

    # Marcar completed_at SIN re-disparar el signal
    sender.objects.filter(pk=instance.pk).update(completed_at=now)

    # ── XP reward de la lección ───────────────────────────────────────────
    xp_reward = getattr(instance.lesson, 'xp_reward', 10)

    stats, _ = UserStats.objects.get_or_create(user=user)

    # ── Actualizar racha basada en fecha ─────────────────────────────────
    today = now.date()

    if stats.last_activity_date is None:
        # Primera actividad del usuario
        stats.current_streak  = 1
    else:
        diff = (today - stats.last_activity_date).days
        if diff == 0:
            # Mismo día: ya contó, no tocar racha
            pass
        elif diff == 1:
            # Día consecutivo: extender racha
            stats.current_streak += 1
        else:
            # Se rompió la racha: reiniciar
            stats.current_streak = 1

    stats.last_activity_date = today

    # Actualizar mejor racha histórica
    if stats.current_streak > stats.longest_streak:
        stats.longest_streak = stats.current_streak

    # Sumar XP DESPUÉS de actualizar streak para que on_stats_updated
    # vea el streak ya actualizado al verificar logros de racha.
    stats.total_xp += xp_reward

    stats.save(update_fields=['total_xp', 'current_streak', 'longest_streak', 'last_activity_date'])

    logger.info('XP +%d → usuario %s | total=%d | streak=%d', xp_reward, user.email, stats.total_xp, stats.current_streak)


# ──────────────────────────────────────────────────────────────────────────────
# 3. Al actualizar stats: verificar y desbloquear logros automáticamente
# ──────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender='learning.UserStats')
def on_stats_updated(sender, instance, **kwargs):
    """
    Verifica todos los logros activos y desbloquea los que el usuario ya cumple.
    Soporta logros por XP, por racha de días y por cursos completados.
    Envía notificación en tiempo real por cada logro desbloqueado.
    """
    from learning.models import Achievement, UserAchievement

    # IDs que el usuario ya tiene — evitar duplicados
    owned_ids = set(
        UserAchievement.objects.filter(user=instance.user)
        .values_list('achievement_id', flat=True)
    )

    unlockable = Achievement.objects.filter(is_active=True).exclude(id__in=owned_ids)

    for ach in unlockable:
        earned = False

        if ach.trigger_type == Achievement.TRIGGER_XP:
            earned = instance.total_xp >= ach.required_xp

        elif ach.trigger_type == Achievement.TRIGGER_STREAK:
            threshold = ach.required_value or ach.required_xp
            earned = instance.current_streak >= threshold

        elif ach.trigger_type == Achievement.TRIGGER_COURSE:
            # Verificar cursos completados del usuario
            from learning.models import UserProgress, Course, Lesson
            threshold = ach.required_value or 1
            completed_courses = 0
            for course in Course.objects.filter(is_active=True):
                total  = Lesson.objects.filter(module__course=course, is_active=True).count()
                if total == 0:
                    continue
                done = UserProgress.objects.filter(
                    user=instance.user,
                    status='completed',
                    lesson__module__course=course,
                ).count()
                if done >= total:
                    completed_courses += 1
            earned = completed_courses >= threshold

        elif ach.trigger_type == Achievement.TRIGGER_MANUAL:
            # Solo se desbloquea manualmente desde el admin
            earned = False

        if earned:
            ua, created = UserAchievement.objects.get_or_create(
                user=instance.user,
                achievement=ach,
            )
            if created:
                logger.info('Logro desbloqueado: %s → %s', instance.user.email, ach.name)
                # Notificar en tiempo real
                push_ws_notification(
                    user_id=instance.user.id,
                    title=f'🏅 Logro desbloqueado: {ach.name}',
                    message=ach.description,
                    notif_type='system',
                )


# ──────────────────────────────────────────────────────────────────────────────
# 4. (ELIMINADO) - El modelo de suscripciones fue reemplazado por venta directa.
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────────
# 5. Notificar a estudiantes cuando se crea una lección nueva
# ──────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender='learning.Lesson')
def notify_new_lesson(sender, instance, created, **kwargs):
    """
    Notifica a todos los estudiantes con progreso en el curso cuando
    se añade una nueva lección.
    """
    if not created:
        return

    from learning.models import UserProgress, User
    from django.conf import settings

    course = instance.module.course

    student_ids = (
        UserProgress.objects
        .filter(lesson__module__course=course)
        .values_list('user_id', flat=True)
        .distinct()
    )

    students = User.objects.filter(id__in=student_ids, is_active=True)

    for student in students:
        # Notificación en tiempo real + BD
        push_ws_notification(
            user_id=student.id,
            title=f'📚 Nueva lección en {course.title}',
            message=f'Se añadió: "{instance.title}". ¡Continúa tu aprendizaje!',
            notif_type='course',
        )

        # Correo opcional
        try:
            from learning.services.email_service import send_custom_email
            action_url = f'{settings.FRONTEND_URL}/courses/{course.id}'
            send_custom_email(student, f'Nueva lección en {course.title}',
                              f'Se añadió la lección "{instance.title}".',
                              action_url, 'Ver lección')
        except Exception as e:
            logger.warning('Email nueva lección falló para %s: %s', student.email, e)


# ──────────────────────────────────────────────────────────────────────────────
# 8. Al pagar una Orden de compra: Enviar notificación / correo al profesor
# ──────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender='learning.Orden')
def on_order_compra_approved(sender, instance, created, **kwargs):
    """
    Cuando una Orden de Compra cambia a estado='pagada':
    Se notifica al profesor responsable para que envíe el enlace del aula.
    """
    if instance.estado != 'pagada':
        return

    from learning.models import Classroom
    from learning.services.email_service import send_custom_email
    from django.conf import settings

    for detalle in instance.detalles.all():
        producto = detalle.producto
        if producto.curso:
            # Encontrar el aula / profesor del curso
            classroom = Classroom.objects.filter(course=producto.curso, is_active=True).first()
            if classroom:
                teacher = classroom.teacher
                # Notificación en tiempo real al profesor
                push_ws_notification(
                    user_id=teacher.id,
                    title=f'🛒 Venta realizada: {producto.titulo}',
                    message=f'El estudiante {instance.estudiante.email} adquirió el curso. Procede a enviar el enlace del aula.',
                    notif_type='system',
                )
                # Enviar correo electrónico al profesor
                try:
                    subject = f'Nueva venta del curso: {producto.titulo}'
                    message = (
                        f'Hola Profesor {teacher.nombre or teacher.email},\n\n'
                        f'El estudiante {instance.estudiante.email} ({instance.estudiante.nombre or "Sin nombre"}) '
                        f'ha comprado el curso "{producto.titulo}".\n'
                        f'Por favor, envíale el enlace correspondiente al aula.\n\n'
                        f'ID de la Orden: #{instance.id}'
                    )
                    send_custom_email(
                        user=teacher,
                        subject=subject,
                        message=message,
                        action_url=f'{settings.FRONTEND_URL}/teacher/dashboard',
                        action_text='Ir al Dashboard de Profesor'
                    )
                except Exception as email_err:
                    logger.error(f'Error enviando correo al profesor {teacher.email}: {email_err}')

