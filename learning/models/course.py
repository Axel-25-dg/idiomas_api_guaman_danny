from django.db import models
from .language import Language


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
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=2, choices=DIFFICULTY_CHOICES, default='A1')

    class Meta:
        ordering = ['language', 'difficulty_level']

    def __str__(self):
        return f'{self.title} ({self.difficulty_level})'


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text')
    order = models.PositiveIntegerField(default=1)
    xp_reward = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ['module', 'order']
        unique_together = ['module', 'order']

    def __str__(self):
        return f'{self.module.title} - {self.title}'


class Exercise(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    question_text = models.TextField()
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPE_CHOICES)
    correct_answer = models.TextField()

    class Meta:
        ordering = ['lesson', 'id']

    def __str__(self):
        return f'[{self.exercise_type}] {self.question_text[:50]}'
