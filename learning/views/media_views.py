"""
Vistas para Multimedia y Progreso de Reproducción
===================================================
MediaFile      → GET/POST /api/media-files/
MediaProgress  → GET/POST/PATCH /api/media-progress/
               → GET /api/media-progress/resume/{lesson_id}/ — reanudar
"""
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from learning.models import MediaFile, MediaProgress
from learning.serializers.media_serializer import MediaFileSerializer, MediaProgressSerializer
from learning.permissions import IsTeacherOrAdmin, _get_role, ROLE_ADMIN
from learning.pagination import StandardPagination


class MediaFileViewSet(viewsets.ModelViewSet):
    """
    GET    /api/media-files/       — Listar archivos multimedia
    POST   /api/media-files/       — Subir archivo (teacher/admin)
    GET    /api/media-files/{id}/  — Detalle del archivo
    DELETE /api/media-files/{id}/  — Soft-delete (teacher/admin)
    """
    serializer_class   = MediaFileSerializer
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['status', 'storage_provider', 'mime_type']
    search_fields      = ['original_name']
    ordering_fields    = ['created_at', 'size']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return MediaFile.objects.filter(deleted_at__isnull=True).select_related('uploaded_by')

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        media = self.get_object()
        media.soft_delete()
        return Response({'detail': 'Archivo eliminado.'}, status=status.HTTP_200_OK)


class MediaProgressViewSet(viewsets.ModelViewSet):
    """
    GET    /api/media-progress/                          — Mi progreso multimedia
    POST   /api/media-progress/                          — Registrar / iniciar progreso
    PATCH  /api/media-progress/{id}/                     — Actualizar posición
    GET    /api/media-progress/resume/{lesson_id}/       — Reanudar lección
    """
    serializer_class   = MediaProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['lesson', 'completed']
    ordering_fields    = ['last_watched']

    def get_queryset(self):
        return MediaProgress.objects.filter(user=self.request.user).select_related('lesson')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Upsert: si ya existe progreso para esa lección, actualizarlo."""
        lesson_id = request.data.get('lesson')
        existing  = MediaProgress.objects.filter(
            user=request.user, lesson_id=lesson_id
        ).first()
        if existing:
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path=r'resume/(?P<lesson_id>[0-9]+)')
    def resume(self, request, lesson_id=None):
        """
        GET /api/media-progress/resume/{lesson_id}/
        Devuelve el progreso actual del usuario en esa lección para reanudar.
        """
        progress = MediaProgress.objects.filter(
            user=request.user, lesson_id=lesson_id
        ).first()
        if not progress:
            return Response(
                {'detail': 'No hay progreso registrado para esta lección.',
                 'position_sec': 0, 'completed': False},
                status=status.HTTP_200_OK,
            )
        return Response(MediaProgressSerializer(progress).data)
