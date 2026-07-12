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
    EmailLog,
    BroadcastEmail,
    MaintenanceLog, BackupHistory, UserActivityLog, UserFavorite,
    Report, UserFeedback, MediaAsset, Announcement, 
    Notification, UserNotificationPreference
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
    list_display = ['id', 'subject', 'is_sent']

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