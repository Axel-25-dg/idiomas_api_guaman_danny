from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from learning.models import Language, Course, Module, Lesson, Exercise
from learning.serializers import (
    LanguageSerializer, CourseSerializer,
    ModuleSerializer, LessonSerializer, ExerciseSerializer,
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
    queryset           = Course.objects.select_related('language').all()
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
    GET    /api/lessons/          — Autenticado (lectura)
    POST   /api/lessons/          — Teacher o Admin
    PUT    /api/lessons/{id}/     — Teacher o Admin
    DELETE /api/lessons/{id}/     — Teacher o Admin
    """
    queryset           = Lesson.objects.select_related('module').all()
    serializer_class   = LessonSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['module', 'content_type']
    search_fields      = ['title']
    ordering_fields    = ['order', 'xp_reward']


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
