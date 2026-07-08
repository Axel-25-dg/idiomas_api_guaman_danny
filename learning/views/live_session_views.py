"""
Vistas para Videotutoría / Sesiones en Vivo
============================================
LiveSession     → GET/POST /api/live-sessions/
LiveParticipant → POST     /api/live-sessions/{id}/join/
                  POST     /api/live-sessions/{id}/leave/
                  GET      /api/live-sessions/{id}/participants/
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from learning.models import LiveSession, LiveParticipant
from learning.serializers.live_session_serializer import (
    LiveSessionSerializer, LiveSessionDetailSerializer, LiveParticipantSerializer,
)
from learning.permissions import IsTeacherOrAdmin, _get_role, ROLE_STUDENT
from learning.pagination import StandardPagination


class LiveSessionViewSet(viewsets.ModelViewSet):
    """
    GET    /api/live-sessions/              — Listar sesiones
    POST   /api/live-sessions/              — Crear sesión (teacher/admin)
    GET    /api/live-sessions/{id}/         — Detalle con participantes
    PATCH  /api/live-sessions/{id}/         — Actualizar (teacher/admin)
    DELETE /api/live-sessions/{id}/         — Cancelar (teacher/admin)
    POST   /api/live-sessions/{id}/join/    — Unirse a sesión (student)
    POST   /api/live-sessions/{id}/leave/   — Salir de sesión
    GET    /api/live-sessions/{id}/participants/ — Lista de participantes
    POST   /api/live-sessions/{id}/start/   — Iniciar sesión (teacher)
    POST   /api/live-sessions/{id}/end/     — Finalizar sesión (teacher)
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['status', 'course', 'teacher']
    search_fields      = ['title', 'description']
    ordering_fields    = ['scheduled_at', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LiveSessionDetailSerializer
        return LiveSessionSerializer

    def get_queryset(self):
        return LiveSession.objects.select_related(
            'teacher', 'course'
        ).prefetch_related('participants').all()

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'start', 'end'):
            return [IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        session = serializer.save()
        # Notificar a todos los estudiantes inscritos en el curso (si tiene)
        if session.course:
            from learning.models import ClassroomEnrollment
            from learning.utils.notify import push_notification
            enrolled = ClassroomEnrollment.objects.filter(
                classroom__course=session.course, is_active=True
            ).select_related('student').exclude(student=session.teacher)
            for enrollment in enrolled:
                push_notification(
                    user       = enrollment.student,
                    title      = 'Nueva sesión en vivo',
                    message    = f'{session.teacher.username} ha programado: {session.title}',
                    notif_type = 'live_session',
                )

    def destroy(self, request, *args, **kwargs):
        session = self.get_object()
        session.status = 'cancelled'
        session.save(update_fields=['status'])
        return Response({'detail': 'Sesión cancelada.'}, status=status.HTTP_200_OK)

    # ── Unirse a sesión ──────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='join',
            permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        """POST /api/live-sessions/{id}/join/ — Student se une"""
        session = self.get_object()
        if session.status not in ('scheduled', 'live'):
            return Response(
                {'detail': 'La sesión no está disponible para unirse.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        active_count = session.participants.filter(is_active=True).count()
        if active_count >= session.max_students:
            return Response(
                {'detail': 'La sesión ha alcanzado su capacidad máxima.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        participant, created = LiveParticipant.objects.get_or_create(
            session=session,
            student=request.user,
            defaults={'is_active': True},
        )
        if not created:
            participant.is_active = True
            participant.left_at   = None
            participant.save(update_fields=['is_active', 'left_at'])
        return Response(
            LiveParticipantSerializer(participant).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    # ── Salir de sesión ──────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='leave',
            permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, pk=None):
        """POST /api/live-sessions/{id}/leave/ — Registrar salida"""
        session = self.get_object()
        try:
            participant = LiveParticipant.objects.get(
                session=session, student=request.user, is_active=True
            )
            participant.is_active = False
            participant.left_at   = timezone.now()
            participant.save(update_fields=['is_active', 'left_at'])
            return Response({'detail': 'Has salido de la sesión.'})
        except LiveParticipant.DoesNotExist:
            return Response(
                {'detail': 'No estás en esta sesión.'},
                status=status.HTTP_404_NOT_FOUND,
            )

    # ── Lista de participantes ───────────────────────────────────────────────
    @action(detail=True, methods=['get'], url_path='participants')
    def participants(self, request, pk=None):
        """GET /api/live-sessions/{id}/participants/"""
        session    = self.get_object()
        qs         = session.participants.select_related('student').all()
        serializer = LiveParticipantSerializer(qs, many=True)
        return Response(serializer.data)

    # ── Iniciar sesión (teacher) ─────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='start',
            permission_classes=[IsTeacherOrAdmin])
    def start(self, request, pk=None):
        """POST /api/live-sessions/{id}/start/ — Cambiar status a 'live'"""
        session = self.get_object()
        if session.status != 'scheduled':
            return Response(
                {'detail': f'No se puede iniciar una sesión con estado "{session.status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.status = 'live'
        session.save(update_fields=['status'])
        return Response({'detail': 'Sesión iniciada.', 'status': 'live'})

    # ── Finalizar sesión (teacher) ───────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='end',
            permission_classes=[IsTeacherOrAdmin])
    def end(self, request, pk=None):
        """POST /api/live-sessions/{id}/end/ — Cambiar status a 'ended'"""
        session = self.get_object()
        if session.status != 'live':
            return Response(
                {'detail': f'No se puede finalizar una sesión con estado "{session.status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.status = 'ended'
        session.save(update_fields=['status'])
        # Marcar todos los participantes activos como inactivos
        session.participants.filter(is_active=True).update(
            is_active=False, left_at=timezone.now()
        )
        return Response({'detail': 'Sesión finalizada.', 'status': 'ended'})
