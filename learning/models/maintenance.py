from django.db import models
from django.conf import settings

class MaintenanceLog(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('IN_PROGRESS', 'In Progress'),
    ]

    permormed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='maintenance_tasks'
    )
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Maintenance Log'
        verbose_name_plural = 'Maintenance Logs'

class BackupHistory(models.Model):
    backup_name = models.CharField(max_length=150)
    file_path = models.CharField(max_length=512)
    size = models.BigIntegerField(help_text="Tamaño en bytes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Backup History'
        verbose_name_plural = 'Backup Histories'