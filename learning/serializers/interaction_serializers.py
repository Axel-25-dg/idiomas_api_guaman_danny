from rest_framework import serializers
from learning.models import Report, UserFeedback, MediaAsset, UserFavorite, UserActivityLog

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
        # Cambiado 'user' por 'uploaded_by' 
        fields = ['id', 'uploaded_by', 'file_name', 'file_type', 'file_url', 'created_at']
        read_only_fields = ['uploaded_by', 'created_at']
class UserFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavorite
        fields = ['id', 'user', 'course', 'lesson', 'created_at']
        read_only_fields = ['user', 'created_at']

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityLog
        # Sincronizado con los modelos (user, module, lesson)
        fields = ['id', 'user', 'module', 'lesson', 'created_at']
        read_only_fields = ['user', 'created_at']