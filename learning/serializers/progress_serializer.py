from rest_framework import serializers
from learning.models import UserProgress, UserStats, Achievement, UserAchievement


class GameSubmissionSerializer(serializers.Serializer):
    game_id = serializers.CharField(max_length=100)
    score = serializers.IntegerField(min_value=0)
    is_win = serializers.BooleanField(required=False, default=False)


class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title    = serializers.CharField(source='lesson.title', read_only=True)
    lesson_xp       = serializers.IntegerField(source='lesson.xp_reward', read_only=True)
    user_email      = serializers.EmailField(source='user.email', read_only=True)
    course_title    = serializers.CharField(source='lesson.module.course.title', read_only=True)
    language_code   = serializers.CharField(source='lesson.module.course.language.code', read_only=True)

    class Meta:
        model  = UserProgress
        fields = [
            'id', 'user', 'user_email',
            'lesson', 'lesson_title', 'lesson_xp',
            'course_title', 'language_code',
            'status', 'score', 'completed_at',
        ]
        read_only_fields = ['user', 'completed_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserStatsSerializer(serializers.ModelSerializer):
    user_email           = serializers.EmailField(source='user.email', read_only=True)
    level                = serializers.IntegerField(read_only=True)
    xp_for_next_level    = serializers.IntegerField(read_only=True)
    xp_progress_in_level = serializers.IntegerField(read_only=True)

    class Meta:
        model  = UserStats
        fields = [
            'id', 'user', 'user_email',
            'total_xp', 'level', 'xp_for_next_level', 'xp_progress_in_level',
            'current_streak', 'longest_streak', 'last_activity_date',
        ]
        read_only_fields = ['user', 'last_activity_date']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Achievement
        fields = [
            'id', 'name', 'description', 'icon_url',
            'required_xp', 'trigger_type', 'required_value', 'is_active', 'created_at',
        ]


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    user_email  = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model  = UserAchievement
        fields = ['id', 'user', 'user_email', 'achievement', 'unlocked_at']
        read_only_fields = ['user', 'unlocked_at']
