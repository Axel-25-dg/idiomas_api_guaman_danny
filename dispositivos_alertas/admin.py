from django.contrib import admin
from .models import UserDevice

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'user', 'operating_system', 'browser', 'last_login', 'is_trusted')
    search_fields = ('device_name', 'user__username', 'user__email')
    list_filter = ('is_trusted', 'operating_system', 'browser')

from .models import UserLocation

@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'country', 'user', 'created_at')
    search_fields = ('city', 'country', 'user__username', 'user__email')
    list_filter = ('country', 'created_at')
