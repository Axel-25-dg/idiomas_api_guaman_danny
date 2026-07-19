from rest_framework import serializers
from learning.models import LiveSession, LiveParticipant


class LiveParticipantSerializer(serializers.ModelSerializer):
    student_email    = serializers.EmailField(source='student.email', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model  = LiveParticipant
        fields = ['id', 'session', 'student', 'student_email', 'student_username',
                  'joined_at', 'left_at', 'is_active']
        read_only_fields = ['student', 'joined_at']


class LiveSessionSerializer(serializers.ModelSerializer):
    teacher_email    = serializers.EmailField(source='teacher.email', read_only=True)
    course_title     = serializers.CharField(source='course.title', read_only=True, default=None)
    status_display   = serializers.CharField(source='get_status_display', read_only=True)
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model  = LiveSession
        fields = ['id', 'teacher', 'teacher_email', 'course', 'course_title',
                  'title', 'description', 'scheduled_at', 'duration_min',
                  'meeting_url', 'status', 'status_display',
                  'max_students', 'participant_count', 'created_at']
        read_only_fields = ['teacher', 'room_id', 'created_at']

    def get_participant_count(self, obj):
        return obj.participants.filter(is_active=True).count()

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class LiveSessionDetailSerializer(LiveSessionSerializer):
    participants = LiveParticipantSerializer(many=True, read_only=True)

    class Meta(LiveSessionSerializer.Meta):
        fields = LiveSessionSerializer.Meta.fields + ['participants']
