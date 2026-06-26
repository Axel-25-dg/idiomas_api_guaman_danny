from django.db import models
from django.conf import settings

class UserDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')
    device_name = models.CharField(max_length=100)
    operating_system = models.CharField(max_length=50)
    browser = models.CharField(max_length=50)
    last_login = models.DateTimeField()
    is_trusted = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_devices'
        verbose_name = 'User Device'
        verbose_name_plural = 'User Devices'

    def __str__(self):
        return f"{self.device_name} ({self.user})"
