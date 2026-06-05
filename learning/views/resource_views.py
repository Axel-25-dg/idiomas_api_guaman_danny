from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from learning.models import TeacherResource
from learning.serializers import TeacherResourceSerializer
from learning.pagination import StandardPagination
from learning.permissions import IsTeacherOrAdmin, IsTeacherOrAdminOrReadOnly, _get_role
from learning.models import ROLE_STUDENT


class TeacherResourceViewSet(viewsets.ModelViewSet):
    """
    Materiales del profesor (PDF, audio, video, Word, imagen, enlace).

    TEACHER / ADMIN:
      GET    /api/resources/           — Todos los recursos públicos + los suyos propios
      POST   /api/resources/           — Subir nuevo recurso
      GET    /api/resources/{id}/      — Detalle
      PUT    /api/resources/{id}/      — Actualizar (solo el dueño o admin)
      DELETE /api/resources/{id}/      — Eliminar (solo el dueño o admin)

    STUDENT:
      GET    /api/resources/           — Solo recursos públicos (is_public=True)
      GET    /api/resources/{id}/      — Detalle de recurso público

    Filtros disponibles:
      ?resource_type=pdf
      ?course=1
      ?lesson=1
      ?is_public=true
      ?search=gramática
    """
    serializer_class   = TeacherResourceSerializer
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['resource_type', 'course', 'lesson', 'is_public']
    search_fields      = ['title', 'description']
    ordering_fields    = ['created_at', 'title', 'resource_type']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        role = _get_role(user)

        if role == ROLE_STUDENT:
            # Estudiantes solo ven recursos públicos
            return TeacherResource.objects.filter(
                is_public=True
            ).select_related('teacher', 'course', 'lesson')

        if user.is_superuser:
            # Admin ve todo
            return TeacherResource.objects.select_related(
                'teacher', 'course', 'lesson'
            ).all()

        # Teacher ve sus propios recursos + los públicos de otros
        return TeacherResource.objects.filter(
            teacher=user
        ).select_related('course', 'lesson') | TeacherResource.objects.filter(
            is_public=True
        ).select_related('teacher', 'course', 'lesson')

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
