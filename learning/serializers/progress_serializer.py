from rest_framework import serializers
from learning.models import UserProgress, UserStats, Achievement, UserAchievement


class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProgress
        fields = ['id', 'user', 'user_email', 'lesson', 'lesson_title', 'status', 'score', 'completed_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserStatsSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserStats
        fields = ['id', 'user', 'user_email', 'total_xp', 'current_streak', 'longest_streak']
        read_only_fields = ['user']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'icon_url', 'required_xp']


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'user_email', 'achievement', 'unlocked_at']
        read_only_fields = ['user', 'unlocked_at']
