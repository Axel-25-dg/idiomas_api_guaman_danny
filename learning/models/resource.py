from django.db import models
from django.conf import settings
from .course import Course, Lesson


RESOURCE_TYPE_CHOICES = [
    ('pdf',       'PDF'),
    ('audio',     'Audio'),
    ('video',     'Video'),
    ('word',      'Documento Word'),
    ('image',     'Imagen'),
    ('link',      'Enlace externo'),
    ('other',     'Otro'),
]


class TeacherResource(models.Model):
    """
    Material subido por un profesor (PDF, audio, video, Word, imagen, enlace).

    El recurso puede vincularse a:
      - Un Course  (material general del curso)
      - Una Lesson (material específico de una lección)
      - Ninguno    (material libre del profesor)

    El campo file_url almacena la URL del archivo ya subido
    (S3, Cloudinary, Google Drive, etc.).
    El backend no gestiona el almacenamiento — recibe la URL final.
    """
    teacher      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resources',
        limit_choices_to={'is_staff': True},
    )
    course       = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources',
        help_text='Curso al que pertenece el recurso (opcional)',
    )
    lesson       = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources',
        help_text='Lección específica (opcional)',
    )
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    resource_type = models.CharField(
        max_length=10,
        choices=RESOURCE_TYPE_CHOICES,
        default='pdf',
    )
    file_url     = models.URLField(
        help_text='URL del archivo (S3, Cloudinary, Google Drive, etc.)',
    )
    is_public    = models.BooleanField(
        default=True,
        help_text='True = visible para todos los estudiantes; False = solo para el aula asignada',
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        course_str = f' [{self.course.title}]' if self.course else ''
        return f'{self.get_resource_type_display()}: {self.title}{course_str}'
