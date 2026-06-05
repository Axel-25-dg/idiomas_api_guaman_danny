import uuid
from django.db import models
from django.conf import settings
from .course import Course


def generate_access_code():
    """Genera un código de acceso de 8 caracteres en mayúsculas. Ej: 'A3FX9K2T'"""
    return uuid.uuid4().hex[:8].upper()


class Classroom(models.Model):
    """
    Clase virtual creada por un profesor.
    Los estudiantes se unen con el access_code.
    Cada clase está vinculada a un Course.
    """
    teacher     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='classrooms_taught',
        limit_choices_to={'is_staff': True},
    )
    course      = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='classrooms',
    )
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    access_code = models.CharField(
        max_length=8,
        unique=True,
        default=generate_access_code,
        editable=False,
    )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    students    = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ClassroomEnrollment',
        related_name='classrooms_enrolled',
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} [{self.access_code}] — {self.teacher.email}'


class ClassroomEnrollment(models.Model):
    """
    Tabla intermedia entre Classroom y User (estudiante).
    Registra cuándo se unió el estudiante y si está activo.
    """
    classroom   = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='enrollments')
    student     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering        = ['-enrolled_at']
        unique_together = ['classroom', 'student']

    def __str__(self):
        return f'{self.student.email} → {self.classroom.name}'
