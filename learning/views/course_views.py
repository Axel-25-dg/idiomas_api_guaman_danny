from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from learning.models import Language, Course, Module, Lesson, Exercise
from learning.serializers import (
    LanguageSerializer, CourseSerializer,
    ModuleSerializer, LessonSerializer, ExerciseSerializer
)
from learning.pagination import StandardPagination
from learning.permissions import IsAdminOrReadOnly


class LanguageViewSet(viewsets.ModelViewSet):
    """
    GET    /api/languages/        — Lista todos los idiomas
    POST   /api/languages/        — Crea un idioma (solo admin)
    GET    /api/languages/{id}/   — Detalle
    PUT    /api/languages/{id}/   — Actualiza (solo admin)
    DELETE /api/languages/{id}/   — Elimina (solo admin)
    """
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']


class CourseViewSet(viewsets.ModelViewSet):
    """
    GET    /api/courses/          — Lista todos los cursos
    POST   /api/courses/          — Crea un curso (solo admin)
    GET    /api/courses/{id}/     — Detalle del curso
    PUT    /api/courses/{id}/     — Actualiza (solo admin)
    DELETE /api/courses/{id}/     — Elimina (solo admin)
    """
    queryset = Course.objects.select_related('language').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['language', 'difficulty_level']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'difficulty_level']


class ModuleViewSet(viewsets.ModelViewSet):
    """
    GET    /api/modules/          — Lista todas las unidades
    POST   /api/modules/          — Crea una unidad (solo admin)
    GET    /api/modules/{id}/     — Detalle
    PUT    /api/modules/{id}/     — Actualiza (solo admin)
    DELETE /api/modules/{id}/     — Elimina (solo admin)
    """
    queryset = Module.objects.select_related('course').all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course']
    search_fields = ['title']
    ordering_fields = ['order', 'title']


class LessonViewSet(viewsets.ModelViewSet):
    """
    GET    /api/lessons/          — Lista todas las lecciones
    POST   /api/lessons/          — Crea una lección (solo admin)
    GET    /api/lessons/{id}/     — Detalle de la lección
    PUT    /api/lessons/{id}/     — Actualiza (solo admin)
    DELETE /api/lessons/{id}/     — Elimina (solo admin)
    """
    queryset = Lesson.objects.select_related('module').all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['module', 'content_type']
    search_fields = ['title']
    ordering_fields = ['order', 'xp_reward']


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    GET    /api/exercises/        — Lista todos los ejercicios
    POST   /api/exercises/        — Crea un ejercicio (solo admin)
    GET    /api/exercises/{id}/   — Detalle
    PUT    /api/exercises/{id}/   — Actualiza (solo admin)
    DELETE /api/exercises/{id}/   — Elimina (solo admin)
    """
    queryset = Exercise.objects.select_related('lesson').all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['lesson', 'exercise_type']
    search_fields = ['question_text']
