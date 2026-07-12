import uuid
from pathlib import Path
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from .language import Language


def course_image_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f'courses/{uuid.uuid4()}{ext}'


DIFFICULTY_CHOICES = [
    ('A1', 'Principiante A1'),
    ('A2', 'Elemental A2'),
    ('B1', 'Intermedio B1'),
    ('B2', 'Intermedio Alto B2'),
    ('C1', 'Avanzado C1'),
    ('C2', 'Maestría C2'),
]

CONTENT_TYPE_CHOICES = [
    ('video', 'Video'),
    ('text', 'Texto'),
    ('interactive', 'Interactivo'),
    ('audio', 'Audio'),
]

EXERCISE_TYPE_CHOICES = [
    ('multiple_choice', 'Opción múltiple'),
    ('translate', 'Traducir'),
    ('listen', 'Escuchar'),
    ('fill_blank', 'Completar espacio'),
    ('match', 'Emparejar'),
]


class Course(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=2, choices=DIFFICULTY_CHOICES, default='A1', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to=course_image_path, blank=True, null=True)
    image_file = models.ForeignKey(
        'learning.MediaFile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='course_images',
    )

    class Meta:
        ordering = ['language', 'difficulty_level']
        constraints = [
            models.UniqueConstraint(fields=['language', 'title'], name='unique_course_title_per_language'),
        ]
        indexes = [
            models.Index(fields=['language', 'difficulty_level']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f'{self.title} ({self.difficulty_level})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Module(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    order = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        constraints = [
            models.UniqueConstraint(fields=['course', 'title'], name='unique_module_title_per_course'),
        ]
        indexes = [models.Index(fields=['course', 'order'])]

    def __str__(self):
        return f'{self.course.title} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Lesson(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text', db_index=True)
    order = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    xp_reward = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    image_file = models.ForeignKey(
        'learning.MediaFile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='lesson_images',
    )

    class Meta:
        ordering = ['module', 'order']
        unique_together = ['module', 'order']
        constraints = [
            models.UniqueConstraint(fields=['module', 'title'], name='unique_lesson_title_per_module'),
        ]
        indexes = [models.Index(fields=['module', 'order'])]

    def __str__(self):
        return f'{self.module.title} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Exercise(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    question_text = models.TextField()
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPE_CHOICES, db_index=True)
    correct_answer = models.TextField()
    options = models.JSONField(null=True, blank=True, help_text="Opciones para opción múltiple")
    audio_url = models.URLField(max_length=500, null=True, blank=True, help_text="URL para ejercicios de tipo listening")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['lesson', 'id']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(exercise_type__in=['multiple_choice', 'translate', 'listen', 'fill_blank', 'match']),
                name='valid_exercise_type',
            ),
        ]
        indexes = [models.Index(fields=['lesson', 'exercise_type'])]

    def __str__(self):
        return f'[{self.exercise_type}] {self.question_text[:50]}'