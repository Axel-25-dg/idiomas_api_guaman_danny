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
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'language', 'language_name', 'title', 'description',
            'difficulty_level', 'image', 'image_url'
        ]
        extra_kwargs = {'image': {'write_only': True}}

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def validate_image(self, value):
        if not value:
            return value
        max_size = 2 * 1024 * 1024  # 2 MB
        valid_types = ['image/jpeg', 'image/png', 'image/webp']
        if value.size > max_size:
            raise serializers.ValidationError('La imagen no debe exceder los 2 MB.')
        if value.content_type not in valid_types:
            raise serializers.ValidationError('Solo se permiten imágenes JPEG, PNG y WebP.')
        return value


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
