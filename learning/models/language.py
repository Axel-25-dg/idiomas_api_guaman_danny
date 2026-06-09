from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Language(models.Model):
    name = models.CharField(max_length=100)          # Ej: "Inglés"
    code = models.CharField(max_length=10, unique=True)  # Ej: "EN"
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    flag_icon_url = models.URLField(blank=True, null=True)
    flag_image = models.ForeignKey(
        'learning.MediaFile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='language_flags',
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['slug']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['code'], name='unique_language_code'),
        ]

    def __str__(self):
        return f'{self.name} ({self.code})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def flag_image_url(self):
        if self.flag_image and self.flag_image.file:
            return self.flag_image.file.url
        return self.flag_icon_url
