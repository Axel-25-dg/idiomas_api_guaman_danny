from rest_framework import serializers
from learning.models import Announcement, Notification, UserNotificationPreference

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'author', 'title', 'content', 'start_date', 'end_date', 'is_active', 'created_at']
        read_only_fields = ['author', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = ['user', 'title', 'message', 'created_at']

class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPreference
        fields = ['email_notifications', 'app_notifications', 'sms_notifications']
