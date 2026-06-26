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
