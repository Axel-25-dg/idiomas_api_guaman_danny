from rest_framework import serializers
from learning.models import MaintenanceLog, BackupHistory, UserActivityLog

class MaintenanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceLog
        fields = ['id', 'performed_by', 'description', 'status', 'created_at']
        read_only_fields = ['performed_by', 'created_at']

class BackupHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupHistory
        fields = ['id', 'backup_name', 'file_path', 'size', 'created_at']
        read_only_fields = ['backup_name', 'file_path', 'size', 'created_at']

