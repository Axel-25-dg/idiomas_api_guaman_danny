from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from learning.models import Classroom, ClassroomEnrollment, ClassroomJoinRequest, Notification
from learning.serializers import (
    ClassroomSerializer, ClassroomDetailSerializer,
    ClassroomEnrollmentSerializer, JoinClassroomSerializer,
    ClassroomJoinRequestSerializer,
)
from learning.pagination import StandardPagination
from learning.permissions import IsTeacherOrAdmin, IsTeacher, _get_role
from learning.models import ROLE_STUDENT
from learning.services.email_service import send_custom_email


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
        try:
            with open("DEBUG_CLASSROOM.txt", "a") as f:
                f.write(f"user={user} role={role} action={self.action} pk={self.kwargs.get('pk')}\n")
        except:
            pass
        if role == ROLE_STUDENT:
            qs = Classroom.objects.filter(
                enrollments__student=user,
                enrollments__is_active=True,
            ).select_related('teacher', 'course').prefetch_related('enrollments').distinct()
            try:
                with open("DEBUG_CLASSROOM.txt", "a") as f:
                    f.write(f"student qs matched={qs.count()}\n")
            except:
                pass
            return qs
        if user.is_superuser:
            return Classroom.objects.select_related(
                'teacher', 'course'
            ).prefetch_related('enrollments').all()
        # Teacher ve solo sus clases
        return Classroom.objects.filter(
            teacher=user
        ).select_related('course').prefetch_related('enrollments')

    def get_permissions(self):
        if self.action in ('join', 'mine', 'retrieve', 'request_join', 'requests', 'approve_request', 'reject_request'):
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

    @action(detail=False, methods=['post'], url_path='request-join',
            permission_classes=[permissions.IsAuthenticated])
    def request_join(self, request):
        classroom_id = request.data.get('classroom_id')
        message = request.data.get('message', '')
        if not classroom_id:
            return Response({'detail': 'Se requiere classroom_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            classroom = Classroom.objects.get(id=classroom_id, is_active=True)
        except Classroom.DoesNotExist:
            return Response({'detail': 'Clase no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        req, created = ClassroomJoinRequest.objects.get_or_create(
            classroom=classroom,
            student=request.user,
            defaults={'message': message, 'status': ClassroomJoinRequest.STATUS_PENDING},
        )
        if not created and req.status == ClassroomJoinRequest.STATUS_APPROVED:
            return Response({'detail': 'Ya tienes acceso a esta clase.'}, status=status.HTTP_200_OK)

        if created:
            Notification.objects.create(
                user=classroom.teacher,
                title='Nueva solicitud para unirse a tu clase',
                message=f'{request.user.email} quiere unirse a {classroom.name}.',
                type='course',
            )
            try:
                send_custom_email(
                    classroom.teacher,
                    'Nueva solicitud de ingreso a clase',
                    f'{request.user.email} quiere unirse a {classroom.name}.',
                )
            except Exception:
                pass

        return Response({'detail': 'Solicitud enviada. Espera la aprobación del profesor.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='requests',
            permission_classes=[permissions.IsAuthenticated])
    def requests(self, request, pk=None):
        classroom = self.get_object()
        if classroom.teacher_id != request.user.id and not request.user.is_superuser:
            return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        qs = ClassroomJoinRequest.objects.filter(classroom=classroom).select_related('student')
        serializer = ClassroomJoinRequestSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='approve-request',
            permission_classes=[permissions.IsAuthenticated])
    def approve_request(self, request, pk=None):
        classroom = self.get_object()
        request_id = request.data.get('request_id')
        if classroom.teacher_id != request.user.id and not request.user.is_superuser:
            return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            join_request = ClassroomJoinRequest.objects.get(id=request_id, classroom=classroom)
        except ClassroomJoinRequest.DoesNotExist:
            return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        join_request.status = ClassroomJoinRequest.STATUS_APPROVED
        join_request.save(update_fields=['status', 'updated_at'])
        ClassroomEnrollment.objects.get_or_create(classroom=classroom, student=join_request.student, defaults={'is_active': True})
        try:
            send_custom_email(
                join_request.student,
                'Tu solicitud para entrar a la clase fue aprobada',
                f'Ya puedes entrar a {classroom.name}. Tu código de acceso es {classroom.access_code}.',
            )
        except Exception:
            pass
        return Response({'detail': 'Solicitud aprobada.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject-request',
            permission_classes=[permissions.IsAuthenticated])
    def reject_request(self, request, pk=None):
        classroom = self.get_object()
        request_id = request.data.get('request_id')
        if classroom.teacher_id != request.user.id and not request.user.is_superuser:
            return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            join_request = ClassroomJoinRequest.objects.get(id=request_id, classroom=classroom)
        except ClassroomJoinRequest.DoesNotExist:
            return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        join_request.status = ClassroomJoinRequest.STATUS_REJECTED
        join_request.save(update_fields=['status', 'updated_at'])
        return Response({'detail': 'Solicitud rechazada.'}, status=status.HTTP_200_OK)

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
