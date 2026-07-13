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
    file = serializers.FileField(required=False, allow_null=True)

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
            'content_type',
            'file',
            'image',
            'file_url',
            'external_url',
            'is_public',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['teacher', 'created_at', 'updated_at']

    def validate(self, attrs):
        # Obligar asociación a curso — no permitir recursos sin course
        course = attrs.get('course')
        if course is None:
            raise serializers.ValidationError(
                {'course': 'Este campo es requerido. Todo recurso debe estar asociado a un curso.'}
            )

        # Si se indica lesson, verificar que pertenece al course indicado
        lesson = attrs.get('lesson')
        if lesson and course and lesson.module.course != course:
            raise serializers.ValidationError(
                'La lección seleccionada no pertenece al curso indicado.'
            )

        content_type = attrs.get('content_type', getattr(self.instance, 'content_type', 'file'))
        file = attrs.get('file')
        external_url = attrs.get('external_url')
        file_url = attrs.get('file_url')

        if content_type == 'file' and not file and not getattr(self.instance, 'file', None) and not file_url and not getattr(self.instance, 'file_url', None):
            raise serializers.ValidationError({'file': 'Este recurso tipo archivo requiere un archivo o una URL válida.'})

        if content_type == 'url' and not external_url and not file_url and not getattr(self.instance, 'external_url', None):
            raise serializers.ValidationError({'external_url': 'Este recurso tipo URL requiere un enlace externo.'})

        if content_type == 'video' and not external_url and not file_url and not getattr(self.instance, 'external_url', None):
            raise serializers.ValidationError({'external_url': 'Este recurso tipo video requiere una URL válida.'})

        return attrs

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)
