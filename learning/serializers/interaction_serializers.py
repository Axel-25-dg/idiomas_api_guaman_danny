from rest_framework import serializers
from learning.models import Report, UserFeedback, MediaAsset, UserFavorite

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'user', 'report_type', 'description', 'status', 'created_at']
        read_only_fields = ['user', 'status', 'created_at']

class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ['id', 'user', 'subject', 'message', 'status', 'created_at']
        read_only_fields = ['user', 'status', 'created_at']

class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ['id', 'user', 'file_name', 'file_type', 'file_url', 'created_at']
        read_only_fields = ['user', 'created_at']

class UserFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavorite
        fields = ['id', 'user', 'course', 'lesson', 'created_at']
        read_only_fields = ['user', 'created_at']