from django.db import models
from django.conf import settings

class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_resets')
    token = models.CharField(max_length=255)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'password_resets'
        verbose_name = 'Password Reset'
        verbose_name_plural = 'Password Resets'

    def __str__(self):
        return f"Password Reset for {self.user} - Used: {self.is_used}"

class LoginAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='login_attempts')
    email = models.EmailField(max_length=150)
    ip_address = models.GenericIPAddressField()
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login_attempts'
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'

    def __str__(self):
        return f"Login Attempt for {self.email} from {self.ip_address}"

class ActiveSession(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='active_sessions')
    device_name = models.CharField(max_length=100)
    browser = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    last_activity = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'active_sessions'
        verbose_name = 'Active Session'
        verbose_name_plural = 'Active Sessions'

    def __str__(self):
        return f"Session for {self.user} on {self.device_name}"


class BlockedIp(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255)
    blocked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blocked_ips'
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'

    def __str__(self):
        return f"{self.ip_address} - {self.reason}"

class ApiToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_tokens')
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_tokens'
        verbose_name = 'API Token'
        verbose_name_plural = 'API Tokens'

    def __str__(self):
        return f"Token for {self.user} (Active: {self.is_active})"


class BiometricDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='biometric_devices')
    device_id = models.CharField(max_length=255, help_text="ID único del dispositivo (ej. UUID)")
    biometric_token = models.CharField(max_length=255, unique=True, help_text="Token secreto generado por el backend")
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'biometric_devices'
        verbose_name = 'Biometric Device'
        verbose_name_plural = 'Biometric Devices'
        unique_together = ('user', 'device_id')

    def __str__(self):
        return f"Biometric Device for {self.user} ({self.device_id})"
