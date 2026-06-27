from rest_framework import viewsets, permissions
from learning.models import Announcement, Notification, UserNotificationPreference
from learning.serializers.notification_serializers import (
    AnnouncementSerializer, 
    NotificationSerializer, 
    UserNotificationPreferenceSerializer
)

class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    """Solo lectura para usuarios, para evitar ediciones no autorizadas."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Announcement.objects.filter(is_active=True)
    serializer_class = AnnouncementSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # Seguridad: un usuario no debe ver las notificaciones de otro
        return self.queryset.filter(user=self.request.user)

class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserNotificationPreference.objects.all()
    serializer_class = UserNotificationPreferenceSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)