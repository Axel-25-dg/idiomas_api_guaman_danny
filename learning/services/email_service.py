import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now

from learning.models import EmailLog

logger = logging.getLogger(__name__)


def _create_log(recipient, subject, template_name, status='pending', response=None):
    return EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        template_name=template_name,
        status=status,
        response=response,
        sent_at=None,
    )


def _send_email(recipient, subject, template_name, context, attachments=None):
    html_body = render_to_string(template_name, context)
    text_body = strip_tags(html_body)
    from_email = settings.DEFAULT_FROM_EMAIL
    email_log = _create_log(recipient, subject, template_name)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[recipient],
    )
    message.attach_alternative(html_body, 'text/html')

    if attachments:
        for attachment in attachments:
            message.attach(attachment['filename'], attachment['content'], attachment.get('mime_type', 'application/octet-stream'))

    try:
        message.send(fail_silently=False)
        email_log.status = 'sent'
        email_log.sent_at = now()
        email_log.response = 'OK'
        email_log.save(update_fields=['status', 'sent_at', 'response'])
    except Exception as exc:
        logger.exception('Error enviando correo a %s', recipient)
        email_log.status = 'failed'
        email_log.response = str(exc)
        email_log.sent_at = now()
        email_log.save(update_fields=['status', 'sent_at', 'response'])
        raise

    return email_log


def send_welcome_email(user):
    context = {
        'user': user,
        'subject': 'Bienvenido a la plataforma de idiomas',
    }
    return _send_email(
        recipient=user.email,
        subject='Bienvenido a JumpUp UTE',
        template_name='emails/welcome_email.html',
        context=context,
    )


def send_verification_email(user, verification_link):
    context = {
        'user': user,
        'verification_link': verification_link,
        'subject': 'Verifica tu correo electrónico',
    }
    return _send_email(
        recipient=user.email,
        subject='Por favor verifica tu correo electrónico',
        template_name='emails/verification_email.html',
        context=context,
    )


def send_password_reset_email(user, reset_link):
    context = {
        'user': user,
        'reset_link': reset_link,
        'subject': 'Restablece tu contraseña',
    }
    return _send_email(
        recipient=user.email,
        subject='Restablece tu contraseña',
        template_name='emails/password_reset_email.html',
        context=context,
    )


def send_certificate_email(user, certificate, download_link=None):
    context = {
        'user': user,
        'certificate': certificate,
        'download_link': download_link,
        'subject': 'Tu certificado está listo',
    }
    return _send_email(
        recipient=user.email,
        subject='Certificado emitido',
        template_name='emails/certificate_email.html',
        context=context,
    )


def send_course_notification(user, course, message):
    context = {
        'user': user,
        'course': course,
        'message': message,
        'subject': 'Notificación de curso',
    }
    return _send_email(
        recipient=user.email,
        subject=f'Actualización del curso {course.title}',
        template_name='emails/course_notification_email.html',
        context=context,
    )


def send_payment_confirmation(user, payment):
    context = {
        'user': user,
        'payment': payment,
        'subject': 'Confirmación de pago',
    }
    return _send_email(
        recipient=user.email,
        subject='Pago confirmado',
        template_name='emails/payment_confirmation_email.html',
        context=context,
    )


def send_subscription_expiration(user, subscription, expiration_date):
    context = {
        'user': user,
        'subscription': subscription,
        'expiration_date': expiration_date,
        'subject': 'Suscripción próxima a vencer',
    }
    return _send_email(
        recipient=user.email,
        subject='Tu suscripción está a punto de vencer',
        template_name='emails/subscription_expiration_email.html',
        context=context,
    )
