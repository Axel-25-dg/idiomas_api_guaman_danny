from rest_framework import serializers
from learning.models import Announcement, Notification, UserNotificationPreference


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Announcement
        fields = ['id', 'author', 'title', 'content', 'start_date', 'end_date', 'is_active', 'created_at']
        read_only_fields = ['author', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model  = Notification
        fields = [
            'id', 'uuid', 'user', 'title', 'message',
            'type', 'type_display', 'is_read', 'created_at',
        ]
        read_only_fields = ['uuid', 'user', 'title', 'message', 'type', 'created_at']


class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserNotificationPreference
        fields = ['email_notifications', 'app_notifications', 'sms_notifications']
