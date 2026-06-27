from rest_framework import viewsets, permissions
from learning.models import MaintenanceLog, BackupHistory
from learning.serializers.system_serializers import MaintenanceLogSerializer, BackupHistorySerializer

class MaintenanceLogViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer

class BackupHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = BackupHistory.objects.all()
    serializer_class = BackupHistorySerializer

