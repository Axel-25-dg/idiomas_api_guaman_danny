from django.contrib import admin
from .models import PasswordReset, LoginAttempt, ActiveSession, BlockedIp, ApiToken, BiometricDevice


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'is_used', 'expires_at', 'created_at']
    list_filter   = ['is_used']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['token', 'created_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display  = ['id', 'email', 'ip_address', 'attempts', 'created_at']
    search_fields = ['email', 'ip_address']
    list_filter   = ['created_at']
    readonly_fields = ['created_at']


@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'device_name', 'browser', 'ip_address', 'is_active', 'last_activity']
    list_filter   = ['is_active', 'browser']
    search_fields = ['user__email', 'ip_address', 'device_name']


@admin.register(BlockedIp)
class BlockedIpAdmin(admin.ModelAdmin):
    list_display  = ['id', 'ip_address', 'reason', 'blocked_until', 'created_at']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['created_at']


@admin.register(ApiToken)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'is_active', 'expires_at', 'created_at']
    list_filter   = ['is_active']
    search_fields = ['user__email']
    readonly_fields = ['token', 'created_at']


@admin.register(BiometricDevice)
class BiometricDeviceAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'device_id', 'is_active', 'created_at', 'last_used']
    list_filter   = ['is_active']
    search_fields = ['user__email', 'device_id']
    readonly_fields = ['biometric_token', 'created_at']
