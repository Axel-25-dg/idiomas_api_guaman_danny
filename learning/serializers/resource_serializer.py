from rest_framework import serializers
from learning.models import TeacherResource


class TeacherResourceSerializer(serializers.ModelSerializer):
    """
    Serializer completo de TeacherResource para lectura y escritura.
    """
    teacher_email      = serializers.EmailField(source='teacher.email',   read_only=True)
    course_title       = serializers.CharField(source='course.title',     read_only=True, default=None)
    lesson_title       = serializers.CharField(source='lesson.title',     read_only=True, default=None)
    resource_type_display = serializers.CharField(
        source='get_resource_type_display', read_only=True
    )

    class Meta:
        model  = TeacherResource
        fields = [
            'id',
            'teacher',
            'teacher_email',
            'course',
            'course_title',
            'lesson',
            'lesson_title',
            'title',
            'description',
            'resource_type',
            'resource_type_display',
            'file_url',
            'is_public',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['teacher', 'created_at', 'updated_at']

    def validate(self, attrs):
        # Si se indica lesson, verificar que pertenece al course indicado
        lesson = attrs.get('lesson')
        course = attrs.get('course')
        if lesson and course and lesson.module.course != course:
            raise serializers.ValidationError(
                'La lección seleccionada no pertenece al curso indicado.'
            )
        return attrs

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)
