"""
Dashboard endpoints — Resúmenes consolidados por rol.

GET /api/dashboard/student/  → Resumen gamificación + progreso del estudiante
GET /api/dashboard/teacher/  → Métricas del profesor
GET /api/dashboard/admin/    → Estadísticas globales de la plataforma
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from learning.models import (
    User, UserStats, UserProgress, UserAchievement, Certificate,
    Classroom, ClassroomEnrollment, Lesson, Course,
    TeacherResource, OrdenCompra,
)
from learning.permissions import IsTeacherOrAdmin, IsAdmin


class StudentDashboardView(APIView):
    """
    GET /api/dashboard/student/
    Resumen completo del estudiante autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Stats
        stats, _ = UserStats.objects.get_or_create(user=user)
        xp = stats.total_xp
        level = (xp // 100) + 1

        # Progreso
        total_lessons = Lesson.objects.count()
        completed_lessons = UserProgress.objects.filter(
            user=user, status='completed'
        ).count()
        progress_percentage = round(
            (completed_lessons / total_lessons * 100), 1
        ) if total_lessons > 0 else 0.0

        # Logros y certificados
        achievements_count = UserAchievement.objects.filter(user=user).count()
        certificates_count = Certificate.objects.filter(
            student=user, status='issued'
        ).count()

        # Clases activas
        active_classrooms = ClassroomEnrollment.objects.filter(
            student=user, is_active=True
        ).count()

        return Response({
            'total_xp':             xp,
            'level':                level,
            'xp_progress':          xp % 100,
            'xp_for_next_level':    level * 100,
            'current_streak':       stats.current_streak,
            'longest_streak':       stats.longest_streak,
            'progress_percentage':  progress_percentage,
            'completed_lessons':    completed_lessons,
            'total_lessons':        total_lessons,
            'achievements_count':   achievements_count,
            'certificates_count':   certificates_count,
            'active_classrooms':    active_classrooms,
        })


class TeacherDashboardView(APIView):
    """
    GET /api/dashboard/teacher/
    Métricas del profesor autenticado.
    """
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        user = request.user

        classrooms = Classroom.objects.filter(teacher=user)
        classrooms_count = classrooms.count()

        # Total de estudiantes únicos inscritos en sus clases
        students_count = ClassroomEnrollment.objects.filter(
            classroom__teacher=user,
            is_active=True,
        ).values('student').distinct().count()

        # Recursos del profesor
        resources_count = TeacherResource.objects.filter(teacher=user).count()

        # Lecciones creadas (en módulos de cursos que tienen sus clases)
        # Simplificado: contar lecciones de los cursos vinculados a sus clases
        course_ids = classrooms.values_list('course_id', flat=True).distinct()
        lessons_count = Lesson.objects.filter(
            module__course_id__in=course_ids
        ).count()

        # Certificados emitidos por este profesor
        certificates_count = Certificate.objects.filter(issued_by=user).count()

        return Response({
            'classrooms':    classrooms_count,
            'students':      students_count,
            'resources':     resources_count,
            'lessons':       lessons_count,
            'certificates':  certificates_count,
        })


class AdminDashboardView(APIView):
    """
    GET /api/dashboard/admin/
    Estadísticas globales de la plataforma.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        from learning.models import ROLE_TEACHER, ROLE_STUDENT

        total_users = User.objects.filter(is_active=True).count()
        teachers = User.objects.filter(
            is_active=True, role__name=ROLE_TEACHER
        ).count()
        students = User.objects.filter(
            is_active=True, role__name=ROLE_STUDENT
        ).count()
        courses = Course.objects.count()
        classrooms = Classroom.objects.count()
        ventas = OrdenCompra.objects.filter(estado='pagada').count()
        certificates = Certificate.objects.filter(status='issued').count()

        return Response({
            'users':          total_users,
            'teachers':       teachers,
            'students':       students,
            'courses':        courses,
            'classrooms':     classrooms,
            'ventas_directas': ventas,
            'certificates':   certificates,
        })
