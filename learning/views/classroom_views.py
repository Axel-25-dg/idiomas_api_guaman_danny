from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from learning.models import Classroom, ClassroomEnrollment
from learning.serializers import (
    ClassroomSerializer, ClassroomDetailSerializer,
    ClassroomEnrollmentSerializer, JoinClassroomSerializer,
)
from learning.pagination import StandardPagination
from learning.permissions import IsTeacherOrAdmin, IsTeacher, _get_role
from learning.models import ROLE_STUDENT


class ClassroomViewSet(viewsets.ModelViewSet):
    """
    Gestión de clases virtuales.

    TEACHER / ADMIN:
      GET    /api/classrooms/           — Lista sus propias clases (teacher) o todas (admin)
      POST   /api/classrooms/           — Crear clase (teacher o admin)
      GET    /api/classrooms/{id}/      — Detalle con lista de estudiantes
      PUT    /api/classrooms/{id}/      — Actualizar
      DELETE /api/classrooms/{id}/      — Eliminar
      POST   /api/classrooms/{id}/remove-student/  — Expulsar estudiante

    STUDENT:
      POST   /api/classrooms/join/      — Unirse con access_code
      GET    /api/classrooms/mine/      — Ver clases en las que está inscrito
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['is_active', 'course']
    search_fields      = ['name', 'description']
    ordering_fields    = ['created_at', 'name']

    def get_serializer_class(self):
        # Detalle → serializer extendido con enrollments
        if self.action == 'retrieve':
            return ClassroomDetailSerializer
        return ClassroomSerializer

    def get_queryset(self):
        user = self.request.user
        role = _get_role(user)
        if role == ROLE_STUDENT:
            # El estudiante no debería llegar aquí directamente,
            # pero por seguridad devolvemos vacío
            return Classroom.objects.none()
        if user.is_superuser:
            return Classroom.objects.select_related('teacher', 'course').all()
        # Teacher ve solo sus clases
        return Classroom.objects.filter(teacher=user).select_related('course')

    def get_permissions(self):
        if self.action in ('join', 'mine'):
            return [permissions.IsAuthenticated()]
        return [IsTeacherOrAdmin()]

    # ── Acción: unirse a una clase con código ────────────────────────────────
    @action(detail=False, methods=['post'], url_path='join',
            permission_classes=[permissions.IsAuthenticated])
    def join(self, request):
        """
        POST /api/classrooms/join/
        Body: { "access_code": "A3FX9K2T" }
        El estudiante se une a la clase. Si ya estaba inscrito, reactiva la inscripción.
        """
        serializer = JoinClassroomSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        classroom = serializer.save()
        return Response(
            ClassroomSerializer(classroom, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    # ── Acción: mis clases (para el estudiante) ──────────────────────────────
    @action(detail=False, methods=['get'], url_path='mine',
            permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        """
        GET /api/classrooms/mine/
        Clases en las que el estudiante está inscrito y activas.
        """
        classrooms = Classroom.objects.filter(
            enrollments__student=request.user,
            enrollments__is_active=True,
            is_active=True,
        ).select_related('teacher', 'course').distinct()
        page = self.paginate_queryset(classrooms)
        if page is not None:
            serializer = ClassroomSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ClassroomSerializer(classrooms, many=True, context={'request': request})
        return Response(serializer.data)

    # ── Acción: expulsar estudiante ──────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='remove-student',
            permission_classes=[IsTeacherOrAdmin])
    def remove_student(self, request, pk=None):
        """
        POST /api/classrooms/{id}/remove-student/
        Body: { "student_id": 5 }
        El profesor desactiva la inscripción del estudiante.
        """
        classroom  = self.get_object()
        student_id = request.data.get('student_id')

        if not student_id:
            return Response(
                {'detail': 'Se requiere student_id.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            enrollment = ClassroomEnrollment.objects.get(
                classroom=classroom, student_id=student_id
            )
            enrollment.is_active = False
            enrollment.save(update_fields=['is_active'])
            return Response({'detail': 'Estudiante removido de la clase.'})
        except ClassroomEnrollment.DoesNotExist:
            return Response(
                {'detail': 'El estudiante no está inscrito en esta clase.'},
                status=status.HTTP_404_NOT_FOUND,
            )
