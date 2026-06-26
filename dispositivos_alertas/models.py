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

class UserLocation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='locations')
    country = models.CharField(max_length=60)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_locations'
        verbose_name = 'User Location'
        verbose_name_plural = 'User Locations'

    def __str__(self):
        return f"{self.city}, {self.country} ({self.user})"
