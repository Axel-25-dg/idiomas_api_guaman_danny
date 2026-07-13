from rest_framework import serializers
from learning.models import Classroom, ClassroomEnrollment, ClassroomJoinRequest, User
from learning.serializers.user_serializer import UserSerializer
from learning.serializers.course_serializer import CourseSerializer


class ClassroomEnrollmentSerializer(serializers.ModelSerializer):
    student_email    = serializers.EmailField(source='student.email', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model  = ClassroomEnrollment
        fields = ['id', 'student', 'student_email', 'student_username', 'enrolled_at', 'is_active']
        read_only_fields = ['enrolled_at']


class ClassroomSerializer(serializers.ModelSerializer):
    """
    Serializer principal de Classroom.
    - teacher_email: solo lectura, informativo.
    - course_title:  solo lectura, informativo.
    - total_students: conteo calculado.
    - access_code: solo lectura (se genera automáticamente).
    """
    teacher_email  = serializers.EmailField(source='teacher.email', read_only=True)
    course_title   = serializers.CharField(source='course.title',   read_only=True)
    total_students = serializers.SerializerMethodField()

    class Meta:
        model  = Classroom
        fields = [
            'id',
            'name',
            'description',
            'course',
            'course_title',
            'teacher',
            'teacher_email',
            'access_code',
            'is_active',
            'total_students',
            'created_at',
        ]
        read_only_fields = ['teacher', 'access_code', 'created_at']

    def get_total_students(self, obj):
        return obj.enrollments.filter(is_active=True).count()

    def create(self, validated_data):
        # El teacher siempre es el usuario autenticado
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class ClassroomDetailSerializer(ClassroomSerializer):
    """
    Serializer extendido con lista de estudiantes inscritos (solo activos).
    Usado en GET /api/classrooms/{id}/ por el profesor.
    """
    enrollments = serializers.SerializerMethodField()

    class Meta(ClassroomSerializer.Meta):
        fields = ClassroomSerializer.Meta.fields + ['enrollments']

    def get_enrollments(self, obj):
        active_enrollments = obj.enrollments.filter(is_active=True).select_related('student')
        return ClassroomEnrollmentSerializer(active_enrollments, many=True).data


class ClassroomJoinRequestSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source='student.email', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)

    class Meta:
        model = ClassroomJoinRequest
        fields = ['id', 'classroom', 'classroom_name', 'student', 'student_email', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['student', 'status', 'created_at', 'updated_at']


class JoinClassroomSerializer(serializers.Serializer):
    """
    Serializer para que un estudiante se una a una clase con el access_code.
    POST /api/classrooms/join/
    """
    access_code = serializers.CharField(max_length=8, min_length=8)

    def validate_access_code(self, value):
        value = value.upper().strip()
        try:
            classroom = Classroom.objects.get(access_code=value, is_active=True)
        except Classroom.DoesNotExist:
            raise serializers.ValidationError(
                'Código de acceso inválido o la clase no está activa.'
            )
        self.classroom = classroom
        return value

    def save(self, **kwargs):
        student   = self.context['request'].user
        classroom = self.classroom

        enrollment, created = ClassroomEnrollment.objects.get_or_create(
            classroom=classroom,
            student=student,
            defaults={'is_active': True},
        )

        if not created and not enrollment.is_active:
            enrollment.is_active = True
            enrollment.save(update_fields=['is_active'])

        return classroom
