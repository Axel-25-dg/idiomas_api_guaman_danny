from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from learning.models import Announcement, Notification, UserNotificationPreference
from learning.serializers.notification_serializers import (
    AnnouncementSerializer,
    NotificationSerializer,
    UserNotificationPreferenceSerializer,
)
from learning.pagination import StandardPagination


class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    """Solo lectura para usuarios, para evitar ediciones no autorizadas."""
    permission_classes = [permissions.IsAuthenticated]
    queryset           = Announcement.objects.filter(is_active=True)
    serializer_class   = AnnouncementSerializer
    pagination_class   = StandardPagination


class NotificationViewSet(viewsets.ModelViewSet):
    """
    GET    /api/notifications/              — Mis notificaciones
    GET    /api/notifications/?is_read=false — No leídas
    GET    /api/notifications/?type=course  — Por tipo
    POST   /api/notifications/{id}/read/    — Marcar una como leída
    POST   /api/notifications/read-all/     — Marcar todas como leídas
    GET    /api/notifications/unread-count/ — Cantidad no leídas
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = NotificationSerializer
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['is_read', 'type']
    ordering_fields    = ['created_at']
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        """POST /api/notifications/{id}/read/ — Marcar una notificación como leída"""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'detail': 'Notificación marcada como leída.'})

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        """POST /api/notifications/read-all/ — Marcar todas como leídas"""
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({'detail': f'{updated} notificaciones marcadas como leídas.'})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """GET /api/notifications/unread-count/ — Cantidad de no leídas"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})


class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset           = UserNotificationPreference.objects.all()
    serializer_class   = UserNotificationPreferenceSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)