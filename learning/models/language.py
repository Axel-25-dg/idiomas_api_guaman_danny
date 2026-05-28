from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=100)          # Ej: "Inglés"
    code = models.CharField(max_length=10, unique=True)  # Ej: "EN"
    flag_icon_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'
