from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms

from learning.models import (
    Role, User, UserProfile,
    Language, Course, Module, Lesson, Exercise,
    UserProgress, UserStats, Achievement, UserAchievement,
    Classroom, ClassroomEnrollment,
    Certificate,
    TeacherResource,
    MediaFile,
    EmailLog,
    BroadcastEmail,
    MaintenanceLog, BackupHistory, UserActivityLog, UserFavorite,
    Report, UserFeedback, MediaAsset, Announcement,
    Notification, UserNotificationPreference,
    MessageThread, Message, MessageAttachment,
    ForumCategory, ForumThread, ForumPost, ForumReaction, ForumReport,
    SocialPost, SocialComment, SocialReaction,
    LiveSession, LiveParticipant,
    MediaProgress,
    Catalogo, Carrito, CarritoItem, OrdenCompra, OrdenDetalle,
)
from learning.services.email_service import send_custom_email, send_broadcast_email

# ─── Formularios personalizados ────────────────────────────────────────────────

class SendEmailForm(forms.Form):
    subject = forms.CharField(label="Asunto", max_length=200, widget=forms.TextInput(attrs={'style': 'width: 100%;'}))
    message = forms.CharField(label="Mensaje", widget=forms.Textarea(attrs={'rows': 10, 'style': 'width: 100%;'}))
    action_url = forms.URLField(label="URL del botón (Opcional)", required=False, widget=forms.URLInput(attrs={'style': 'width: 100%;'}))
    action_text = forms.CharField(label="Texto del botón (Opcional)", required=False, max_length=50, widget=forms.TextInput(attrs={'style': 'width: 100%;'}))

# ─── Configuración general ────────────────────────────────────────────────────
admin.site.site_header  = "JumpUp UTE — Administración"
admin.site.site_title   = "JumpUp UTE Admin"
admin.site.index_title  = "Panel de Control"

# ─── ROLES ────────────────────────────────────────────────────────────────────
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display   = ['id', 'name', 'total_users']
    search_fields  = ['name']
    ordering       = ['name']

    def total_users(self, obj):
        return obj.users.count()
    total_users.short_description = 'Usuarios'

# ─── USUARIOS ─────────────────────────────────────────────────────────────────
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display   = ['id', 'email', 'username', 'role_badge', 'is_staff', 'is_superuser', 'is_active', 'created_at']
    list_filter    = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields  = ['email', 'username']
    ordering       = ['-created_at']
    readonly_fields = ['created_at']
    fieldsets      = BaseUserAdmin.fieldsets + (('Rol y acceso', {'fields': ('role', 'created_at')}),)
    actions = ['send_custom_email_action']

    def send_custom_email_action(self, request, queryset):
        if 'apply' in request.POST:
            form = SendEmailForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
                action_url = form.cleaned_data['action_url']
                action_text = form.cleaned_data['action_text']
                count = 0
                for user in queryset:
                    try:
                        send_custom_email(user, subject, message, action_url, action_text)
                        count += 1
                    except Exception: pass
                self.message_user(request, f"Se han enviado {count} correos.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = SendEmailForm()
        return render(request, 'admin/send_email_form.html', context={'users': queryset, 'form': form})
    
    send_custom_email_action.short_description = "Enviar correo personalizado"

    def role_badge(self, obj):
        colors = {'admin': '#dc3545', 'teacher': '#fd7e14', 'student': '#198754'}
        role_name = obj.role.name if obj.role else 'sin rol'
        color = colors.get(role_name, '#6c757d')
        return format_html('<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold">{}</span>', color, role_name.upper())
    role_badge.short_description = 'Rol'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'native_language', 'timezone']

# ─── IDIOMAS Y CURSOS ──────────────────────────────────────────────────────────
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'language', 'difficulty_level']

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'order']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'module', 'content_type', 'order']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['id', 'lesson', 'exercise_type']

# ─── PROGRESO Y LOGROS ────────────────────────────────────────────────────────
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'lesson', 'status', 'score']

@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_xp', 'current_streak']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'required_xp']

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'achievement']

# ─── CLASSROOMS Y CERTIFICADOS ────────────────────────────────────────────────
@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'teacher', 'course', 'is_active']

@admin.register(ClassroomEnrollment)
class ClassroomEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'classroom']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['id', 'certificate_code', 'student', 'status']

# ─── LOGS Y OTROS ─────────────────────────────────────────────────────────────
@admin.register(TeacherResource)
class TeacherResourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'teacher', 'resource_type']

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'subject', 'status']

@admin.register(BroadcastEmail)
class BroadcastEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'audience', 'sent_count', 'is_sent', 'sent_at', 'created_at']
    list_filter    = ['is_sent', 'audience']
    search_fields  = ['subject']
    readonly_fields = ['is_sent', 'sent_count', 'sent_at', 'created_at', 'updated_at']
    actions        = ['send_broadcast_action']

    def sent_badge(self, obj):
        if obj.is_sent:
            return format_html('<span style="background:#198754;color:#fff;padding:2px 10px;border-radius:4px;font-size:11px;font-weight:bold">ENVIADO</span>')
        return format_html('<span style="background:#fd7e14;color:#fff;padding:2px 10px;border-radius:4px;font-size:11px;font-weight:bold">PENDIENTE</span>')
    sent_badge.short_description = 'Estado'

    def send_broadcast_action(self, request, queryset):
        """
        Acción: Enviar correo masivo a todos los usuarios activos.
        Selecciona uno o varios BroadcastEmail y usa esta acción.
        """
        for broadcast in queryset:
            if broadcast.is_sent:
                self.message_user(
                    request,
                    f'"{broadcast.subject}" ya fue enviado anteriormente.',
                    level=messages.WARNING,
                )
                continue
            try:
                send_broadcast_email(broadcast)
                # send_broadcast_email ya marca is_sent=True y guarda sent_count
                # Recargamos para obtener el conteo actualizado
                broadcast.refresh_from_db()
                self.message_user(
                    request,
                    f'"{broadcast.subject}" enviado a {broadcast.sent_count} usuarios.',
                    level=messages.SUCCESS,
                )
            except Exception as e:
                self.message_user(
                    request,
                    f'Error enviando "{broadcast.subject}": {e}',
                    level=messages.ERROR,
                )
    send_broadcast_action.short_description = 'Enviar correo masivo a todos los usuarios activos'

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'report_type', 'status']

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'file_type']

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status']

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'module', 'lesson']

@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_active']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'is_read']

@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email_notifications', 'app_notifications']

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'performed_by', 'status']

@admin.register(BackupHistory)
class BackupHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'backup_name', 'size']

# ─── ARCHIVOS MULTIMEDIA ──────────────────────────────────────────────────────
@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display  = ['id', 'original_name', 'mime_type', 'extension', 'size', 'status', 'storage_provider', 'uploaded_by']
    list_filter   = ['status', 'storage_provider', 'mime_type']
    search_fields = ['original_name', 'uploaded_by__email']
    readonly_fields = ['uuid', 'checksum', 'created_at']

# ─── MENSAJERÍA ───────────────────────────────────────────────────────────────
@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display  = ['id', 'subject', 'is_active', 'created_at', 'updated_at']
    list_filter   = ['is_active']
    search_fields = ['subject']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ['id', 'sender', 'thread', 'is_read', 'created_at']
    list_filter   = ['is_read']
    search_fields = ['sender__email', 'body']
    readonly_fields = ['created_at', 'read_at']

@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display  = ['id', 'message', 'attachment_type', 'filename', 'created_at']
    list_filter   = ['attachment_type']
    search_fields = ['filename']

# ─── FORO ─────────────────────────────────────────────────────────────────────
@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'order', 'is_active', 'created_at']
    list_filter   = ['is_active']
    search_fields = ['name']

@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display  = ['id', 'title', 'category', 'author', 'is_pinned', 'is_closed', 'views', 'created_at']
    list_filter   = ['is_pinned', 'is_closed', 'category']
    search_fields = ['title', 'author__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display  = ['id', 'author', 'thread', 'is_deleted', 'created_at']
    list_filter   = ['is_deleted']
    search_fields = ['author__email', 'body']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ForumReaction)
class ForumReactionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'post', 'reaction', 'created_at']
    list_filter   = ['reaction']
    search_fields = ['user__email']

@admin.register(ForumReport)
class ForumReportAdmin(admin.ModelAdmin):
    list_display  = ['id', 'reporter', 'post', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['reporter__email', 'reason']

# ─── FEED SOCIAL ──────────────────────────────────────────────────────────────
@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display  = ['id', 'author', 'post_type', 'is_public', 'created_at']
    list_filter   = ['post_type', 'is_public']
    search_fields = ['author__email', 'content']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SocialComment)
class SocialCommentAdmin(admin.ModelAdmin):
    list_display  = ['id', 'author', 'post', 'created_at']
    search_fields = ['author__email', 'body']

@admin.register(SocialReaction)
class SocialReactionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'post', 'reaction', 'created_at']
    list_filter   = ['reaction']
    search_fields = ['user__email']

# ─── SESIONES EN VIVO ─────────────────────────────────────────────────────────
@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'title', 'teacher', 'course', 'status', 'scheduled_at', 'max_students']
    list_filter   = ['status']
    search_fields = ['title', 'teacher__email']
    readonly_fields = ['created_at']

@admin.register(LiveParticipant)
class LiveParticipantAdmin(admin.ModelAdmin):
    list_display  = ['id', 'student', 'session', 'is_active', 'joined_at']
    list_filter   = ['is_active']
    search_fields = ['student__email']

# ─── PROGRESO MULTIMEDIA ──────────────────────────────────────────────────────
@admin.register(MediaProgress)
class MediaProgressAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'lesson', 'position_sec', 'duration_sec', 'completed', 'last_watched']
    list_filter   = ['completed']
    search_fields = ['user__email', 'lesson__title']

# ─── VENTAS / E-COMMERCE ──────────────────────────────────────────────────────
@admin.register(Catalogo)
class CatalogoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'titulo', 'tipo', 'precio', 'curso', 'creado_at']
    list_filter   = ['tipo']
    search_fields = ['titulo']

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'estudiante', 'creado_at']
    search_fields = ['estudiante__email']

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display  = ['id', 'carrito', 'producto', 'cantidad']
    search_fields = ['carrito__estudiante__email', 'producto__titulo']

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display  = ['id', 'estudiante', 'total', 'estado', 'fecha_creacion']
    list_filter   = ['estado']
    search_fields = ['estudiante__email']

@admin.register(OrdenDetalle)
class OrdenDetalleAdmin(admin.ModelAdmin):
    list_display  = ['id', 'orden', 'producto', 'precio_unitario']
    search_fields = ['orden__estudiante__email', 'producto__titulo']
