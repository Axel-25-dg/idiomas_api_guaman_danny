from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms

from learning.models import (
    Role, User, UserProfile,
    Language, Course, Module, Lesson, Exercise,
    UserProgress, UserStats, Achievement, UserAchievement,
    Subscription, UserSubscription, Payment, Order,
    Classroom, ClassroomEnrollment,
    Certificate,
    TeacherResource,
    EmailLog,
    BroadcastEmail,
    #nuevos modelos
    MaintenanceLog, BackupHistory, UserActivityLog, UserFavorite,
    Report, UserFeedback, MediaAsset, Announcement, 
    Notification, UserNotificationPreference
)
from learning.services.email_service import send_custom_email, send_broadcast_email

# ─── Formularios personalizados para el Admin ────────────────────────────────

class SendEmailForm(forms.Form):
    subject = forms.CharField(label="Asunto", max_length=200, widget=forms.TextInput(attrs={'style': 'width: 100%;'}))
    message = forms.CharField(label="Mensaje", widget=forms.Textarea(attrs={'rows': 10, 'style': 'width: 100%;'}))
    action_url = forms.URLField(label="URL del botón (Opcional)", required=False, widget=forms.URLInput(attrs={'style': 'width: 100%;'}))
    action_text = forms.CharField(label="Texto del botón (Opcional)", required=False, max_length=50, widget=forms.TextInput(attrs={'style': 'width: 100%;'}))

# ─── Configuración general del sitio admin ────────────────────────────────────
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

class UserProfileInline(admin.StackedInline):
    """Perfil inline dentro del formulario del usuario."""
    model       = UserProfile
    can_delete  = False
    verbose_name_plural = 'Perfil'
    fields      = ['first_name', 'last_name', 'avatar', 'avatar_url', 'native_language', 'timezone']
    extra       = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # inlines        = [UserProfileInline]
    list_display   = [
        'id', 'email', 'username', 'role_badge',
        'is_staff', 'is_superuser', 'is_active', 'created_at'
    ]
    list_filter    = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields  = ['email', 'username']
    ordering       = ['-created_at']
    readonly_fields = ['created_at']
    fieldsets      = BaseUserAdmin.fieldsets + (
        ('Rol y acceso', {'fields': ('role', 'created_at')}),
    )
    # Al cambiar el role, los flags se sincronizan en User.save()
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
                    except Exception:
                        pass
                
                self.message_user(request, f"Se han enviado {count} correos personalizados.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = SendEmailForm()

        return render(
            request,
            'admin/send_email_form.html',
            context={'users': queryset, 'form': form}
        )
    
    send_custom_email_action.short_description = "Enviar correo personalizado"

    def role_badge(self, obj):
        colors = {
            'admin':   '#dc3545',
            'teacher': '#fd7e14',
            'student': '#198754',
        }
        role_name = obj.role.name if obj.role else 'sin rol'
        color     = colors.get(role_name, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:bold">{}</span>',
            color, role_name.upper()
        )
    role_badge.short_description = 'Rol'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display   = ['id', 'user', 'first_name', 'last_name', 'native_language', 'timezone']
    search_fields  = ['user__email', 'first_name', 'last_name']
    list_filter    = ['native_language', 'timezone']


# ─── IDIOMAS ──────────────────────────────────────────────────────────────────

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display   = ['id', 'name', 'code', 'flag_preview', 'total_courses']
    search_fields  = ['name', 'code']
    ordering       = ['name']

    def flag_preview(self, obj):
        if obj.flag_icon_url:
            return format_html(
                '<img src="{}" style="height:20px;width:auto;" />',
                obj.flag_icon_url
            )
        return '—'
    flag_preview.short_description = 'Bandera'

    def total_courses(self, obj):
        return obj.courses.count()
    total_courses.short_description = 'Cursos'


# ─── CURSOS ───────────────────────────────────────────────────────────────────

class ModuleInline(admin.TabularInline):
    """Módulos inline dentro del formulario de curso."""
    model   = Module
    extra   = 1
    fields  = ['title', 'order']
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines        = [ModuleInline]
    list_display   = ['id', 'title', 'language', 'difficulty_badge', 'total_modules', 'image_preview']
    list_filter    = ['difficulty_level', 'language']
    search_fields  = ['title', 'description']
    ordering       = ['language', 'difficulty_level']

    DIFFICULTY_COLORS = {
        'A1': '#198754', 'A2': '#20c997',
        'B1': '#0dcaf0', 'B2': '#0d6efd',
        'C1': '#fd7e14', 'C2': '#dc3545',
    }

    def difficulty_badge(self, obj):
        color = self.DIFFICULTY_COLORS.get(obj.difficulty_level, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:bold">{}</span>',
            color, obj.difficulty_level
        )
    difficulty_badge.short_description = 'Nivel'

    def total_modules(self, obj):
        return obj.modules.count()
    total_modules.short_description = 'Módulos'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:30px;width:auto;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Imagen'


# ─── MÓDULOS ──────────────────────────────────────────────────────────────────

class LessonInline(admin.TabularInline):
    """Lecciones inline dentro del formulario de módulo."""
    model   = Lesson
    extra   = 1
    fields  = ['title', 'content_type', 'order', 'xp_reward']
    ordering = ['order']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    inlines        = [LessonInline]
    list_display   = ['id', 'title', 'course', 'order', 'total_lessons']
    list_filter    = ['course']
    search_fields  = ['title', 'course__title']
    ordering       = ['course', 'order']

    def total_lessons(self, obj):
        return obj.lessons.count()
    total_lessons.short_description = 'Lecciones'


# ─── LECCIONES ────────────────────────────────────────────────────────────────

class ExerciseInline(admin.TabularInline):
    """Ejercicios inline dentro del formulario de lección."""
    model   = Exercise
    extra   = 1
    fields  = ['exercise_type', 'question_text', 'correct_answer']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    inlines        = [ExerciseInline]
    list_display   = ['id', 'title', 'module', 'content_type', 'order', 'xp_reward']
    list_filter    = ['content_type', 'module__course']
    search_fields  = ['title']
    ordering       = ['module', 'order']


# ─── EJERCICIOS ───────────────────────────────────────────────────────────────

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display   = ['id', 'lesson', 'exercise_type', 'short_question']
    list_filter    = ['exercise_type']
    search_fields  = ['question_text', 'lesson__title']
    ordering       = ['lesson', 'id']

    def short_question(self, obj):
        return obj.question_text[:60] + '…' if len(obj.question_text) > 60 else obj.question_text
    short_question.short_description = 'Pregunta'


# ─── PROGRESO DE USUARIOS ─────────────────────────────────────────────────────

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display   = ['id', 'user', 'lesson', 'status_badge', 'score', 'completed_at']
    list_filter    = ['status']
    search_fields  = ['user__email', 'lesson__title']
    ordering       = ['-completed_at']
    readonly_fields = ['completed_at']

    def status_badge(self, obj):
        colors = {'completed': '#198754', 'in_progress': '#fd7e14'}
        color  = colors.get(obj.status, '#6c757d')
        labels = {'completed': 'Completado', 'in_progress': 'En curso'}
        label  = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Estado'


# ─── ESTADÍSTICAS ─────────────────────────────────────────────────────────────

@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display   = ['id', 'user', 'total_xp', 'current_streak', 'longest_streak']
    search_fields  = ['user__email']
    ordering       = ['-total_xp']


# ─── LOGROS ───────────────────────────────────────────────────────────────────

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display   = ['id', 'name', 'required_xp', 'icon_preview', 'total_unlocked']
    search_fields  = ['name', 'description']
    ordering       = ['required_xp']

    def icon_preview(self, obj):
        if obj.icon_url:
            return format_html(
                '<img src="{}" style="height:24px;width:auto;" />',
                obj.icon_url
            )
        return '—'
    icon_preview.short_description = 'Ícono'

    def total_unlocked(self, obj):
        return obj.users.count()
    total_unlocked.short_description = 'Usuarios con este logro'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display   = ['id', 'user', 'achievement', 'unlocked_at']
    list_filter    = ['achievement']
    search_fields  = ['user__email', 'achievement__name']
    ordering       = ['-unlocked_at']
    readonly_fields = ['unlocked_at']


# ─── SUSCRIPCIONES ────────────────────────────────────────────────────────────

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display   = ['id', 'name', 'price', 'duration_days', 'total_subscribers']
    search_fields  = ['name']
    ordering       = ['price']

    def total_subscribers(self, obj):
        return obj.user_subscriptions.filter(is_active=True).count()
    total_subscribers.short_description = 'Suscritos activos'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display   = ['id', 'user', 'subscription', 'start_date', 'end_date', 'status_badge']
    list_filter    = ['is_active', 'subscription']
    search_fields  = ['user__email']
    ordering       = ['-start_date']

    def status_badge(self, obj):
        color = '#198754' if obj.is_active else '#dc3545'
        label = 'Activa' if obj.is_active else 'Vencida'
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Estado'


# ─── PAGOS ────────────────────────────────────────────────────────────────────

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display   = ['id', 'user', 'amount', 'payment_method', 'status_badge', 'transaction_date']
    list_filter    = ['status', 'payment_method']
    search_fields  = ['user__email']
    ordering       = ['-transaction_date']
    readonly_fields = ['transaction_date']

    # Acción masiva: aprobar pagos seleccionados
    actions = ['approve_payments', 'reject_payments']

    def approve_payments(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} pago(s) aprobado(s).')
    approve_payments.short_description = 'Aprobar pagos seleccionados'

    def reject_payments(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} pago(s) rechazado(s).')
    reject_payments.short_description = 'Rechazar pagos seleccionados'

    def status_badge(self, obj):
        colors = {
            'approved': '#198754',
            'rejected': '#dc3545',
            'pending':  '#fd7e14',
        }
        labels = {
            'approved': 'Aprobado',
            'rejected': 'Rechazado',
            'pending':  'Pendiente',
        }
        color = colors.get(obj.status, '#6c757d')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Estado'


# ─── ÓRDENES ──────────────────────────────────────────────────────────────────

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = [
        'id', 'user', 'subscription', 'total_amount',
        'payment_method', 'status_badge', 'created_at'
    ]
    list_filter    = ['status', 'payment_method', 'subscription']
    search_fields  = ['user__email', 'notes']
    ordering       = ['-created_at']
    readonly_fields = ['created_at']
    actions        = ['mark_approved', 'mark_rejected']

    def mark_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} orden(es) marcada(s) como aprobada(s).')
    mark_approved.short_description = 'Marcar como aprobadas'

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} orden(es) marcada(s) como rechazada(s).')
    mark_rejected.short_description = 'Marcar como rechazadas'

    def status_badge(self, obj):
        colors = {
            'approved': '#198754',
            'rejected': '#dc3545',
            'pending':  '#fd7e14',
        }
        labels = {
            'approved': 'Aprobado',
            'rejected': 'Rechazado',
            'pending':  'Pendiente',
        }
        color = colors.get(obj.status, '#6c757d')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Estado'


# ─── CLASSROOMS ───────────────────────────────────────────────────────────────

class ClassroomEnrollmentInline(admin.TabularInline):
    model        = ClassroomEnrollment
    extra        = 0
    fields       = ['student', 'enrolled_at', 'is_active']
    readonly_fields = ['enrolled_at']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    inlines        = [ClassroomEnrollmentInline]
    list_display   = ['id', 'name', 'teacher', 'course', 'access_code', 'status_badge', 'total_students', 'created_at']
    list_filter    = ['is_active', 'course']
    search_fields  = ['name', 'teacher__email', 'access_code']
    ordering       = ['-created_at']
    readonly_fields = ['access_code', 'created_at']

    def status_badge(self, obj):
        color = '#198754' if obj.is_active else '#dc3545'
        label = 'Activa' if obj.is_active else 'Inactiva'
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Estado'

    def total_students(self, obj):
        return obj.enrollments.filter(is_active=True).count()
    total_students.short_description = 'Alumnos activos'


@admin.register(ClassroomEnrollment)
class ClassroomEnrollmentAdmin(admin.ModelAdmin):
    list_display  = ['id', 'student', 'classroom', 'enrolled_at', 'is_active']
    list_filter   = ['is_active', 'classroom']
    search_fields = ['student__email', 'classroom__name']
    readonly_fields = ['enrolled_at']


# ─── CERTIFICATES ─────────────────────────────────────────────────────────────

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display   = [
        'id', 'certificate_code', 'student', 'level',
        'status_badge', 'issued_by', 'issued_at', 'created_at',
    ]
    list_filter    = ['level', 'status']
    search_fields  = ['certificate_code', 'student__email', 'title']
    ordering       = ['-created_at']
    readonly_fields = ['certificate_code', 'created_at']
    actions        = ['issue_certificates', 'revoke_certificates']

    def issue_certificates(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='issued',
            issued_at=timezone.now(),
            issued_by=request.user,
        )
        self.message_user(request, f'{updated} certificado(s) emitido(s).')
    issue_certificates.short_description = 'Emitir certificados seleccionados'

    def revoke_certificates(self, request, queryset):
        updated = queryset.exclude(status='revoked').update(status='revoked')
        self.message_user(request, f'{updated} certificado(s) revocado(s).')
    revoke_certificates.short_description = 'Revocar certificados seleccionados'

    def status_badge(self, obj):
        colors = {'issued': '#198754', 'pending': '#fd7e14', 'revoked': '#dc3545'}
        labels = {'issued': 'Emitido', 'pending': 'Pendiente', 'revoked': 'Revocado'}
        color  = colors.get(obj.status, '#6c757d')
        label  = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Estado'


# ─── TEACHER RESOURCES ────────────────────────────────────────────────────────

@admin.register(TeacherResource)
class TeacherResourceAdmin(admin.ModelAdmin):
    list_display   = [
        'id', 'title', 'teacher', 'resource_type_badge',
        'course', 'lesson', 'is_public', 'created_at',
    ]
    list_filter    = ['resource_type', 'is_public', 'course']
    search_fields  = ['title', 'description', 'teacher__email']
    ordering       = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    RESOURCE_COLORS = {
        'pdf':   '#dc3545',
        'audio': '#0d6efd',
        'video': '#6f42c1',
        'word':  '#0dcaf0',
        'image': '#198754',
        'link':  '#fd7e14',
        'other': '#6c757d',
    }

    def resource_type_badge(self, obj):
        color = self.RESOURCE_COLORS.get(obj.resource_type, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:bold">{}</span>',
            color, obj.get_resource_type_display().upper()
        )
    resource_type_badge.short_description = 'Tipo'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'subject', 'status', 'sent_at']
    list_filter  = ['status', 'template_name']
    search_fields = ['recipient', 'subject']
    readonly_fields = ['sent_at', 'created_at']


@admin.register(BroadcastEmail)
class BroadcastEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'audience', 'sent_count', 'is_sent', 'sent_at']
    list_filter  = ['audience', 'is_sent']
    search_fields = ['subject', 'message']
    readonly_fields = ['sent_count', 'is_sent', 'sent_at']
    actions = ['execute_broadcast']

    def execute_broadcast(self, request, queryset):
        for broadcast in queryset:
            if not broadcast.is_sent:
                count = send_broadcast_email(broadcast)
                self.message_user(request, f"Envío masivo '{broadcast.subject}' completado: {count} correos enviados.")
            else:
                self.message_user(request, f"El envío '{broadcast.subject}' ya fue procesado anteriormente.", messages.WARNING)
    
    execute_broadcast.short_description = "Ejecutar envío masivo ahora"





# ─── REPORTES Y FEEDBACK ──────────────────────────────────────────

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'report_type', 'status', 'created_at']
    list_filter = ['status', 'report_type']
    search_fields = ['user__email', 'description']

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'file_type', 'uploaded_by', 'created_at']

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['subject', 'message']

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    # Corregido: usando los campos existentes en el modelo
    list_display = ['id', 'user', 'module', 'lesson', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email']

@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'lesson', 'created_at']
    search_fields = ['user__email']



# ─── NOTIFICACIONES Y ANUNCIOS ──────────────────────────────────────

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['user__email', 'title']

@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email_notifications', 'app_notifications', 'sms_notifications']
    search_fields = ['user__email']


# ─── MANTENIMIENTO Y ACTIVIDAD ──────────────────────────────────────

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    # Corregido: 'performed_by'
    list_display = ['id', 'performed_by', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['description']

@admin.register(BackupHistory)
class BackupHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'backup_name', 'size', 'created_at']
    readonly_fields = ['created_at']

