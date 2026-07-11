from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

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
    GET  /api/progress/            — Progreso del usuario autenticado
    POST /api/progress/            — Registrar progreso en una lección
    GET  /api/progress/{id}/       — Detalle
    PUT  /api/progress/{id}/       — Actualizar progreso (ej: marcar completado)
    GET  /api/progress/summary/    — Resumen general (XP, rachas, %)
    GET  /api/progress/by-language/ — Progreso desglosado por idioma
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
        ).select_related('lesson__module__course__language')

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        GET /api/progress/summary/
        Resumen completo del estudiante: lecciones, cursos, XP, rachas, logros.
        """
        user = request.user

        total_lessons = Lesson.objects.filter(is_active=True).count()
        completed     = UserProgress.objects.filter(user=user, status='completed').count()
        in_progress   = UserProgress.objects.filter(user=user, status='in_progress').count()

        courses_started   = (
            UserProgress.objects.filter(user=user)
            .values('lesson__module__course').distinct().count()
        )

        courses_completed = 0
        for course in Course.objects.filter(is_active=True):
            course_lessons = Lesson.objects.filter(module__course=course, is_active=True).count()
            if course_lessons == 0:
                continue
            user_done = UserProgress.objects.filter(
                user=user, status='completed', lesson__module__course=course
            ).count()
            if user_done >= course_lessons:
                courses_completed += 1

        percentage = round((completed / total_lessons * 100), 1) if total_lessons > 0 else 0.0

        stats, _ = UserStats.objects.get_or_create(user=user)

        return Response({
            'total_lessons':        total_lessons,
            'lessons_completed':    completed,
            'lessons_in_progress':  in_progress,
            'courses_started':      courses_started,
            'courses_completed':    courses_completed,
            'percentage':           percentage,
            # Gamificación
            'total_xp':             stats.total_xp,
            'level':                stats.level,
            'xp_for_next_level':    stats.xp_for_next_level,
            'xp_progress_in_level': stats.xp_progress_in_level,
            'current_streak':       stats.current_streak,
            'longest_streak':       stats.longest_streak,
            'last_activity_date':   stats.last_activity_date,
            'achievements_count':   UserAchievement.objects.filter(user=user).count(),
        })

    @action(detail=False, methods=['get'], url_path='by-language')
    def by_language(self, request):
        """
        GET /api/progress/by-language/
        Progreso del usuario desglosado por cada idioma que está aprendiendo.
        Útil para mostrar el panel de idiomas en Flutter.
        """
        user = request.user

        # Idiomas que el usuario está aprendiendo
        if hasattr(user, 'profile'):
            languages = user.profile.languages_learning.filter(is_active=True)
        else:
            from learning.models import Language
            languages = Language.objects.filter(is_active=True)

        result = []
        for lang in languages:
            total = Lesson.objects.filter(
                module__course__language=lang, is_active=True
            ).count()
            done = UserProgress.objects.filter(
                user=user,
                status='completed',
                lesson__module__course__language=lang,
            ).count()
            pct = round((done / total * 100), 1) if total > 0 else 0.0
            result.append({
                'language_id':   lang.id,
                'language_name': lang.name,
                'language_code': lang.code,
                'flag_url':      lang.flag_image_url,
                'total_lessons': total,
                'completed':     done,
                'percentage':    pct,
            })

        return Response(result)


class UserStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/stats/    — Estadísticas del usuario autenticado (objeto único)
    """
    serializer_class   = UserStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserStats.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Devuelve un objeto único en vez de lista paginada."""
        stats, _ = UserStats.objects.get_or_create(user=request.user)
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/achievements/        — Catálogo de logros disponibles
    GET /api/achievements/{id}/   — Detalle
    """
    queryset           = Achievement.objects.filter(is_active=True)
    serializer_class   = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['trigger_type', 'is_active']
    ordering_fields    = ['required_xp', 'name']


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/my-achievements/  — Logros desbloqueados por el usuario autenticado
    """
    serializer_class   = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAchievement.objects.filter(
            user=self.request.user
        ).select_related('achievement')


class RankingViewSet(viewsets.ViewSet):
    """
    GET /api/ranking/               — Top 100 global por XP
    GET /api/ranking/?language=EN   — Top 100 por idioma específico
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter('language', OpenApiTypes.STR, description='Código de idioma (ej: EN, ES)'),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def list(self, request):
        language_code = request.query_params.get('language')

        if language_code:
            # Filtrar usuarios que están aprendiendo ese idioma
            user_ids = (
                User.objects.filter(
                    profile__languages_learning__code__iexact=language_code,
                    is_active=True,
                ).values_list('id', flat=True)
            )
            rankings = (
                UserStats.objects
                .filter(user_id__in=user_ids)
                .select_related('user')
                .order_by('-total_xp')[:100]
            )
        else:
            rankings = (
                UserStats.objects
                .filter(user__is_active=True)
                .select_related('user')
                .order_by('-total_xp')[:100]
            )

        # Posición del usuario actual
        my_stats, _ = UserStats.objects.get_or_create(user=request.user)
        my_position = (
            UserStats.objects
            .filter(user__is_active=True, total_xp__gt=my_stats.total_xp)
            .count() + 1
        )

        data = []
        for position, stat in enumerate(rankings, start=1):
            data.append({
                'position':       position,
                'user_id':        stat.user.id,
                'username':       stat.user.username,
                'email':          stat.user.email,
                'total_xp':       stat.total_xp,
                'level':          stat.level,
                'current_streak': stat.current_streak,
                'longest_streak': stat.longest_streak,
                'is_me':          stat.user_id == request.user.id,
            })

        return Response({
            'my_position': my_position,
            'my_xp':       my_stats.total_xp,
            'my_level':    my_stats.level,
            'ranking':     data,
        })
