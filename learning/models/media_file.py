import os
import uuid
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import SoftDeleteModel, TimestampedModel
from .validators import validate_uploaded_file
from learning.utils.media_utils import generate_media_path, process_media_file


MEDIA_STATUS_CHOICES = [
    ('uploaded', 'Subido'),
    ('processing', 'Procesando'),
    ('active', 'Activo'),
    ('deleted', 'Eliminado'),
]

STORAGE_PROVIDER_CHOICES = [
    ('local', 'Local'),
    ('s3', 'Amazon S3'),
    ('cloudinary', 'Cloudinary'),
]


class MediaFile(SoftDeleteModel, TimestampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to=generate_media_path, max_length=500)
    mime_type = models.CharField(max_length=100, blank=True)
    extension = models.CharField(max_length=10, blank=True)
    size = models.PositiveBigIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=64, unique=True, blank=True, null=True, db_index=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', null=True, blank=True, max_length=500)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='uploaded_media_files',
    )
    storage_provider = models.CharField(
        max_length=20,
        choices=STORAGE_PROVIDER_CHOICES,
        default='local',
    )
    status = models.CharField(
        max_length=20,
        choices=MEDIA_STATUS_CHOICES,
        default='uploaded',
        db_index=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['storage_provider']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.original_name} ({self.mime_type or self.extension})'

    def save(self, *args, **kwargs):
        if self.file and not self.checksum:
            validate_uploaded_file(self.file)
            asset = process_media_file(self.file)
            self.original_name = asset['original_name']
            self.mime_type = asset['mime_type']
            self.extension = asset['extension']
            self.size = asset['size']
            self.checksum = asset['checksum']
            self.width = asset['width']
            self.height = asset['height']
            self.storage_provider = self.storage_provider or settings.STORAGE_PROVIDER
            self.status = 'active'
            filename = os.path.basename(self.original_name)
            if asset['data'] is not None:
                self.file.save(filename, ContentFile(asset['data']), save=False)
            if asset['thumbnail'] is not None:
                thumb_name = f'thumb_{uuid.uuid4().hex}.webp'
                self.thumbnail.save(thumb_name, ContentFile(asset['thumbnail']), save=False)
        super().save(*args, **kwargs)

    @property
    def file_url(self):
        return self.file.url if self.file else None

    @property
    def thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else None
