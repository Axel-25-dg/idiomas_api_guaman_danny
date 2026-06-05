from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count, Sum

from learning.models import (
    Role, User, UserProfile,
    Language, Course, Module, Lesson, Exercise,
    UserProgress, UserStats, Achievement, UserAchievement,
    Subscription, UserSubscription, Payment, Order,
)

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
    fields      = ['first_name', 'last_name', 'avatar_url', 'native_language', 'timezone']
    extra       = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines        = [UserProfileInline]
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
    list_display   = ['id', 'title', 'language', 'difficulty_badge', 'total_modules']
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
