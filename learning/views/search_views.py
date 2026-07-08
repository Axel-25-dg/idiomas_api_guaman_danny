"""
Búsqueda Global
================
GET /api/search/?q=<término>&type=<cursos|lecciones|usuarios|recursos>

Devuelve resultados agrupados por tipo o filtrados por 'type'.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q

from learning.models import (
    Course, Lesson, User, TeacherResource,
    ForumThread, SocialPost, LiveSession,
)
from learning.permissions import _get_role, ROLE_ADMIN


class GlobalSearchView(APIView):
    """
    GET /api/search/?q=python&type=courses

    Parámetros:
      q     (requerido) — texto a buscar (mínimo 2 caracteres)
      type  (opcional)  — cursos | lecciones | usuarios | recursos | foro | sesiones
                          Si se omite, devuelve todos.
      limit (opcional)  — resultados por tipo (default: 5, max: 20)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if len(q) < 2:
            return Response(
                {'detail': 'El término de búsqueda debe tener al menos 2 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        search_type = request.query_params.get('type', 'all').lower()
        limit       = min(int(request.query_params.get('limit', 5)), 20)
        role        = _get_role(request.user)

        results = {}

        # ── Cursos ───────────────────────────────────────────────────────────
        if search_type in ('all', 'cursos', 'courses'):
            courses = Course.objects.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            ).select_related('language').values(
                'id', 'title', 'description', 'difficulty_level',
                'language__name',
            )[:limit]
            results['cursos'] = list(courses)

        # ── Lecciones ────────────────────────────────────────────────────────
        if search_type in ('all', 'lecciones', 'lessons'):
            lessons = Lesson.objects.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            ).select_related('module__course').values(
                'id', 'title', 'description', 'lesson_type',
                'module__title', 'module__course__title',
            )[:limit]
            results['lecciones'] = list(lessons)

        # ── Usuarios (solo admin) ─────────────────────────────────────────────
        if search_type in ('all', 'usuarios', 'users'):
            if role == ROLE_ADMIN:
                users = User.objects.filter(
                    Q(email__icontains=q)
                    | Q(username__icontains=q)
                    | Q(profile__first_name__icontains=q)
                    | Q(profile__last_name__icontains=q)
                ).values('id', 'email', 'username')[:limit]
                results['usuarios'] = list(users)
            else:
                results['usuarios'] = []

        # ── Recursos ─────────────────────────────────────────────────────────
        if search_type in ('all', 'recursos', 'resources'):
            resources = TeacherResource.objects.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            ).select_related('teacher', 'course').values(
                'id', 'title', 'description', 'resource_type',
                'course__title',
            )[:limit]
            results['recursos'] = list(resources)

        # ── Foro ─────────────────────────────────────────────────────────────
        if search_type in ('all', 'foro', 'forum'):
            threads = ForumThread.objects.filter(
                Q(title__icontains=q) | Q(body__icontains=q)
            ).select_related('category', 'author').values(
                'id', 'title', 'category__name', 'author__email', 'views',
            )[:limit]
            results['foro'] = list(threads)

        # ── Sesiones en vivo ─────────────────────────────────────────────────
        if search_type in ('all', 'sesiones', 'sessions'):
            sessions = LiveSession.objects.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            ).select_related('teacher', 'course').values(
                'id', 'title', 'description', 'status',
                'scheduled_at', 'teacher__email',
            )[:limit]
            results['sesiones'] = list(sessions)

        total = sum(len(v) for v in results.values())
        return Response({
            'query':   q,
            'total':   total,
            'results': results,
        })
