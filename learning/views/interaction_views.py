from rest_framework import serializers, viewsets, permissions
from learning.models import Report, UserFeedback, MediaAsset, UserFavorite,UserActivityLog
from learning.serializers.interaction_serializers import (
    ReportSerializer, UserFeedbackSerializer, 
    MediaAssetSerializer, UserFavoriteSerializer, UserActivityLogSerializer,
)

class UserInteractionViewSet(viewsets.ModelViewSet):
    """
    Clase base para asegurar que cualquier interacción (Reporte, Favorito, etc.)
    esté siempre vinculada al usuario que la realizó.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtro de seguridad: el usuario solo ve sus registros
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Inyección: el frontend no envía el 'user', se asigna en el servidor
        serializer.save(user=self.request.user)

class ReportViewSet(UserInteractionViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class UserFeedbackViewSet(UserInteractionViewSet):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer

class MediaAssetViewSet(UserInteractionViewSet):
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    
    def perform_create(self, serializer):
        # Aquí asignamos el usuario al campo correcto 'uploaded_by'
        serializer.save(uploaded_by=self.request.user)

class UserFavoriteViewSet(UserInteractionViewSet):
    queryset = UserFavorite.objects.all()
    serializer_class = UserFavoriteSerializer

class UserActivityLogViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserActivityLog.objects.all()
    serializer_class = UserActivityLogSerializer

