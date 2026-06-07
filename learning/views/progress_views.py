from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Count, Q

from learning.models import (
    UserProgress, UserStats, Achievement, UserAchievement,
    User, Lesson, Course,
)
from learning.serializers import (
    UserProgressSerializer, UserStatsSerializer,
    AchievementSerializer, UserAchievementSerializer,
)
from learning.pagination import StandardPagination


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    GET  /api/progress/       — Progreso del usuario autenticado
    POST /api/progress/       — Registrar progreso en una lección
    GET  /api/progress/{id}/  — Detalle
    PUT  /api/progress/{id}/  — Actualizar progreso
    GET  /api/progress/summary/ — Resumen de progreso (cursos, lecciones, %)
    """
    serializer_class   = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['status', 'lesson']
    ordering_fields    = ['completed_at', 'score']

    def get_queryset(self):
        return UserProgress.objects.filter(
            user=self.request.user
        ).select_related('lesson')

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        GET /api/progress/summary/
        Resumen de progreso del estudiante.
        """
        user = request.user

        total_lessons   = Lesson.objects.count()
        completed       = UserProgress.objects.filter(
            user=user, status='completed'
        ).count()
        in_progress     = UserProgress.objects.filter(
            user=user, status='in_progress'
        ).count()

        # Cursos con al menos una lección completada
        courses_started = UserProgress.objects.filter(
            user=user
        ).values('lesson__module__course').distinct().count()

        # Cursos donde TODAS sus lecciones están completadas
        courses_completed = 0
        for course in Course.objects.all():
            course_lessons = Lesson.objects.filter(module__course=course).count()
            if course_lessons == 0:
                continue
            user_completed = UserProgress.objects.filter(
                user=user,
                status='completed',
                lesson__module__course=course,
            ).count()
            if user_completed >= course_lessons:
                courses_completed += 1

        percentage = round((completed / total_lessons * 100), 1) if total_lessons > 0 else 0.0

        # Stats del usuario
        try:
            stats = UserStats.objects.get(user=user)
            xp = stats.total_xp
            streak = stats.current_streak
            longest = stats.longest_streak
        except UserStats.DoesNotExist:
            xp = 0
            streak = 0
            longest = 0

        level = (xp // 100) + 1
        xp_for_next_level = level * 100
        xp_progress = xp % 100

        return Response({
            'total_lessons':     total_lessons,
            'lessons_completed': completed,
            'lessons_in_progress': in_progress,
            'courses_started':   courses_started,
            'courses_completed': courses_completed,
            'percentage':        percentage,
            'total_xp':          xp,
            'level':             level,
            'xp_for_next_level': xp_for_next_level,
            'xp_progress':       xp_progress,
            'current_streak':    streak,
            'longest_streak':    longest,
            'achievements_count': UserAchievement.objects.filter(user=user).count(),
        })


class UserStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/stats/       — Estadísticas del usuario autenticado
    GET /api/stats/{id}/  — Detalle
    """
    serializer_class   = UserStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserStats.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Override para devolver un objeto único en vez de lista paginada,
        y agregar campos calculados (level, xp_progress).
        """
        stats, _ = UserStats.objects.get_or_create(user=request.user)
        data = UserStatsSerializer(stats).data

        # Campos calculados
        xp = stats.total_xp
        level = (xp // 100) + 1
        data['level'] = level
        data['xp_for_next_level'] = level * 100
        data['xp_progress'] = xp % 100

        return Response(data)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/achievements/       — Lista de todos los logros disponibles
    GET /api/achievements/{id}/  — Detalle del logro
    """
    queryset           = Achievement.objects.all()
    serializer_class   = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [OrderingFilter]
    ordering_fields    = ['required_xp', 'name']


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/my-achievements/  — Logros desbloqueados por el usuario
    """
    serializer_class   = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAchievement.objects.filter(
            user=self.request.user
        ).select_related('achievement')


class RankingViewSet(viewsets.ViewSet):
    """
    GET /api/ranking/ — Top 100 usuarios por XP
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        rankings = UserStats.objects.select_related('user').order_by('-total_xp')[:100]

        data = []
        for position, stat in enumerate(rankings, start=1):
            data.append({
                'position':       position,
                'user_id':        stat.user.id,
                'username':       stat.user.username,
                'email':          stat.user.email,
                'total_xp':       stat.total_xp,
                'level':          (stat.total_xp // 100) + 1,
                'current_streak': stat.current_streak,
                'longest_streak': stat.longest_streak,
            })

        return Response(data)
