from .user import Role, User, UserProfile, ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT, VALID_ROLES
from .language import Language
from .course import Course, Module, Lesson, Exercise
from .progress import UserProgress, UserStats, Achievement, UserAchievement
from .subscription import Subscription, UserSubscription, Payment, Order
from .classroom import Classroom, ClassroomEnrollment
from .certificate import Certificate
from .resource import TeacherResource
from .media_file import MediaFile
from .email_log import EmailLog, BroadcastEmail
from .activities import UserActivityLog, UserFavorite
from .reports import Report, MediaAsset
from .feedback import UserFeedback
# Fuente única de notificaciones — notification.py consolidado
from .notification import (
    Announcement, Notification, UserNotificationPreference, NotificationType,
)
from .maintenance import MaintenanceLog, BackupHistory
from .messaging import MessageThread, Message, MessageAttachment
from .forum import ForumCategory, ForumThread, ForumPost, ForumReaction, ForumReport
from .social import SocialPost, SocialComment, SocialReaction
from .live_session import LiveSession, LiveParticipant
from .media_progress import MediaProgress


__all__ = [
    # Constantes de roles
    'ROLE_ADMIN', 'ROLE_TEACHER', 'ROLE_STUDENT', 'VALID_ROLES',
    # Modelos de usuario
    'Role', 'User', 'UserProfile',
    # Contenido educativo
    'Language',
    'Course', 'Module', 'Lesson', 'Exercise',
    # Progreso y gamificación
    'UserProgress', 'UserStats', 'Achievement', 'UserAchievement',
    # Suscripciones y pagos
    'Subscription', 'UserSubscription', 'Payment', 'Order',
    # Clases y recursos
    'Classroom', 'ClassroomEnrollment',
    'Certificate',
    'TeacherResource',
    # Archivos y logs
    'MediaFile',
    'EmailLog', 'BroadcastEmail',
    # Actividades
    'UserActivityLog', 'UserFavorite',
    'Report', 'MediaAsset',
    'UserFeedback',
    # Notificaciones (fuente única)
    'Announcement', 'Notification', 'UserNotificationPreference', 'NotificationType',
    # Mantenimiento
    'MaintenanceLog', 'BackupHistory',
    # Mensajería
    'MessageThread', 'Message', 'MessageAttachment',
    # Foro
    'ForumCategory', 'ForumThread', 'ForumPost', 'ForumReaction', 'ForumReport',
    # Feed Social
    'SocialPost', 'SocialComment', 'SocialReaction',
    # Videotutoría
    'LiveSession', 'LiveParticipant',
    # Progreso multimedia
    'MediaProgress',
]
