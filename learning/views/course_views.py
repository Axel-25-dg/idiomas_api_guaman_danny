from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Avg, Count, Q

from learning.models import Language, Course, Module, Lesson, Exercise, UserProgress
from learning.serializers import (
    LanguageSerializer, CourseSerializer,
    ModuleSerializer, LessonSerializer, ExerciseSerializer,
    ExerciseSafeSerializer, ExerciseValidationSerializer,
)
from learning.pagination import StandardPagination
from learning.permissions import IsTeacherOrAdminOrReadOnly, IsAdminOrReadOnly


class LanguageViewSet(viewsets.ModelViewSet):
    """
    GET    /api/languages/        — Autenticado (lectura)
    POST   /api/languages/        — Solo admin
    PUT    /api/languages/{id}/   — Solo admin
    DELETE /api/languages/{id}/   — Solo admin

    Los idiomas los gestiona únicamente el admin.
    Los teachers no crean idiomas.
    """
    queryset           = Language.objects.all()
    serializer_class   = LanguageSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [SearchFilter, OrderingFilter]
    search_fields      = ['name', 'code']
    ordering_fields    = ['name', 'code']


class CourseViewSet(viewsets.ModelViewSet):
    """
    GET    /api/courses/          — Autenticado (lectura)
    POST   /api/courses/          — Teacher o Admin
    PUT    /api/courses/{id}/     — Teacher o Admin
    DELETE /api/courses/{id}/     — Teacher o Admin

    Profesores pueden crear y editar cursos.
    """
    queryset           = Course.objects.select_related(
        'language', 'image_file'   # image_file para get_image_url
    ).all()
    serializer_class   = CourseSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['language', 'difficulty_level']
    search_fields      = ['title', 'description']
    ordering_fields    = ['title', 'difficulty_level']


class ModuleViewSet(viewsets.ModelViewSet):
    """
    GET    /api/modules/          — Autenticado (lectura)
    POST   /api/modules/          — Teacher o Admin
    PUT    /api/modules/{id}/     — Teacher o Admin
    DELETE /api/modules/{id}/     — Teacher o Admin
    """
    queryset           = Module.objects.select_related('course').all()
    serializer_class   = ModuleSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['course']
    search_fields      = ['title']
    ordering_fields    = ['order', 'title']


class LessonViewSet(viewsets.ModelViewSet):
    """
    GET    /api/lessons/              — Autenticado (lectura)
    POST   /api/lessons/              — Teacher o Admin
    PUT    /api/lessons/{id}/         — Teacher o Admin
    DELETE /api/lessons/{id}/         — Teacher o Admin
    GET    /api/lessons/{id}/stats/   — Estadísticas de intentos (exámenes interactivos)
    """
    queryset           = Lesson.objects.select_related('module').all()
    serializer_class   = LessonSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['module', 'content_type']
    search_fields      = ['title']
    ordering_fields    = ['order', 'xp_reward']

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        """
        GET /api/lessons/{id}/stats/
        Estadísticas de una lección (útil para lecciones interactivas/exámenes).
        Devuelve: total_attempts, success_rate, average_score
        """
        lesson = self.get_object()

        progress_qs = UserProgress.objects.filter(lesson=lesson)
        total_attempts = progress_qs.count()
        completed = progress_qs.filter(status='completed').count()
        success_rate = round(
            (completed / total_attempts * 100), 1
        ) if total_attempts > 0 else 0.0
        average_score = progress_qs.filter(
            status='completed'
        ).aggregate(avg=Avg('score'))['avg'] or 0.0

        return Response({
            'lesson_id':       lesson.id,
            'lesson_title':    lesson.title,
            'content_type':    lesson.content_type,
            'total_attempts':  total_attempts,
            'completed':       completed,
            'success_rate':    round(success_rate, 1),
            'average_score':   round(average_score, 1),
        })


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    GET    /api/exercises/        — Autenticado (lectura)
    POST   /api/exercises/        — Teacher o Admin
    PUT    /api/exercises/{id}/   — Teacher o Admin
    DELETE /api/exercises/{id}/   — Teacher o Admin
    """
    queryset           = Exercise.objects.select_related('lesson').all()
    serializer_class   = ExerciseSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter]
    filterset_fields   = ['lesson', 'exercise_type']
    search_fields      = ['question_text']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            user = self.request.user
            # Si el usuario no es staff (profesor o administrador), usar serializador seguro (sin respuesta_correcta)
            if user and not user.is_staff:
                return ExerciseSafeSerializer
        elif self.action == 'validar':
            return ExerciseValidationSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'], url_path='validar', permission_classes=[permissions.IsAuthenticated])
    def validar(self, request, pk=None):
        """
        POST /api/exercises/{id}/validar/
        Valida la respuesta del usuario contra respuesta_correcta y actualiza racha/XP.
        """
        exercise = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        respuesta_usuario = serializer.validated_data['respuesta_usuario'].strip()

        es_correcto = (respuesta_usuario.lower() == exercise.correct_answer.strip().lower())

        if es_correcto:
            retroalimentacion = "¡Excelente trabajo! Respuesta correcta."
            user = request.user
            from learning.models import UserStats
            from datetime import date, timedelta
            
            stats, created = UserStats.objects.get_or_create(user=user)
            hoy = date.today()
            
            # Lógica de Rachas (Streak Counter)
            if stats.last_activity_date == hoy:
                # Ya hizo una actividad hoy: la racha no aumenta pero se otorga XP de recompensa
                stats.total_xp += 10
            elif stats.last_activity_date == hoy - timedelta(days=1):
                # Actividad consecutiva: incrementa racha y suma XP
                stats.current_streak += 1
                if stats.current_streak > stats.longest_streak:
                    stats.longest_streak = stats.current_streak
                stats.total_xp += 10
                stats.last_activity_date = hoy
            else:
                # No hubo actividad ayer: racha se reinicia a 1
                stats.current_streak = 1
                stats.total_xp += 10
                stats.last_activity_date = hoy
            stats.save()
        else:
            retroalimentacion = f"Respuesta incorrecta. La respuesta correcta era: '{exercise.correct_answer}'."

        return Response({
            'es_correcto': es_correcto,
            'retroalimentacion': retroalimentacion
        })
