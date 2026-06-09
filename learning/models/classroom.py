import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from .course import Course


def generate_access_code():
    """Genera un código de acceso de 8 caracteres en mayúsculas. Ej: 'A3FX9K2T'"""
    return uuid.uuid4().hex[:8].upper()


class Classroom(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
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
    slug = models.SlugField(max_length=220, blank=True)
    access_code = models.CharField(
        max_length=8,
        unique=True,
        default=generate_access_code,
        editable=False,
    )
    is_active   = models.BooleanField(default=True, db_index=True)
    created_at  = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at  = models.DateTimeField(auto_now=True)
    deleted_at  = models.DateTimeField(null=True, blank=True)
    students    = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ClassroomEnrollment',
        related_name='classrooms_enrolled',
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['teacher', 'course']), models.Index(fields=['access_code'])]

    def __str__(self):
        return f'{self.name} [{self.access_code}] — {self.teacher.email}'

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])


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
    enrolled_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at  = models.DateTimeField(auto_now=True)
    deleted_at  = models.DateTimeField(null=True, blank=True)
    is_active   = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering        = ['-enrolled_at']
        unique_together = ['classroom', 'student']
        indexes = [models.Index(fields=['student', 'classroom'])]

    def __str__(self):
        return f'{self.student.email} → {self.classroom.name}'
