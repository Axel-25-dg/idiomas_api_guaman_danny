from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from learning.models import UserProgress, UserStats, Achievement, UserAchievement
from learning.serializers import (
    UserProgressSerializer, UserStatsSerializer,
    AchievementSerializer, UserAchievementSerializer
)
from learning.pagination import StandardPagination


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    GET  /api/progress/       — Progreso del usuario autenticado
    POST /api/progress/       — Registrar progreso en una lección
    GET  /api/progress/{id}/  — Detalle
    PUT  /api/progress/{id}/  — Actualizar progreso
    """
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'lesson']
    ordering_fields = ['completed_at', 'score']

    def get_queryset(self):
        # Cada usuario solo ve su propio progreso
        return UserProgress.objects.filter(user=self.request.user).select_related('lesson')


class UserStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/stats/       — Estadísticas del usuario autenticado
    GET /api/stats/{id}/  — Detalle
    """
    serializer_class = UserStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserStats.objects.filter(user=self.request.user)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/achievements/       — Lista de todos los logros disponibles
    GET /api/achievements/{id}/  — Detalle del logro
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['required_xp', 'name']


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/my-achievements/  — Logros desbloqueados por el usuario
    """
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user).select_related('achievement')
