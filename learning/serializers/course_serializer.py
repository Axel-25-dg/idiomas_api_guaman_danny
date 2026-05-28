from rest_framework import serializers
from learning.models import Language, Course, Module, Lesson, Exercise


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code', 'flag_icon_url']

    def validate_code(self, value):
        return value.upper()


class CourseSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source='language.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'language', 'language_name', 'title', 'description', 'difficulty_level']


class ModuleSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'course', 'course_title', 'title', 'order']


class LessonSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'module', 'module_title', 'title', 'content_type', 'order', 'xp_reward']


class ExerciseSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Exercise
        fields = ['id', 'lesson', 'lesson_title', 'question_text', 'exercise_type', 'correct_answer']
