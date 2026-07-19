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

RESOURCE_CONTENT_TYPE_CHOICES = [
    ('file', 'Archivo'),
    ('url', 'URL externa'),
    ('video', 'Video embebido'),
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
    content_type = models.CharField(
        max_length=10,
        choices=RESOURCE_CONTENT_TYPE_CHOICES,
        default='file',
        help_text='Tipo de contenido para que Flutter sepa cómo abrirlo.',
    )
    file = models.FileField(
        upload_to='teacher_resources/%Y/%m/%d/',
        null=True,
        blank=True,
        max_length=500,
        help_text='Archivo subido directamente por el profesor.',
    )
    image = models.ImageField(
        upload_to='teacher_resources/images/%Y/%m/%d/',
        null=True,
        blank=True,
        max_length=500,
        help_text='Imagen subida directamente por el profesor.',
    )
    media_file = models.ForeignKey(
        'MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources',
        help_text='Archivo gestionado por la plataforma',
    )
    file_url     = models.URLField(
        null=True,
        blank=True,
        help_text='URL externa o de intercambio; no requerido si se utiliza media_file',
    )
    external_url = models.URLField(
        null=True,
        blank=True,
        help_text='Enlace externo independiente del archivo (solo para recursos tipo link)',
    )
    is_public    = models.BooleanField(
        default=True,
        help_text='True = visible para todos los estudiantes; False = solo para el aula asignada',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='False = recurso desactivado sin borrado físico',
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['resource_type']), models.Index(fields=['is_public']), models.Index(fields=['is_active'])]

    def __str__(self):
        course_str = f' [{self.course.title}]' if self.course else ''
        return f'{self.get_resource_type_display()}: {self.title}{course_str}'
