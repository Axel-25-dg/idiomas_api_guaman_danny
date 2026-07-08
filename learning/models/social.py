"""
Módulo de Feed Social
=====================
SocialPost      → publicación en el feed
SocialComment   → comentario en una publicación
SocialReaction  → reacción (like, love, etc.)
"""
from django.db import models
from django.conf import settings


POST_TYPE_CHOICES = [
    ('achievement', 'Logro desbloqueado'),
    ('certificate', 'Certificado obtenido'),
    ('progress',    'Progreso de curso'),
    ('xp',          'XP acumulado'),
    ('general',     'Publicación general'),
]


class SocialPost(models.Model):
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_posts')
    post_type  = models.CharField(max_length=15, choices=POST_TYPE_CHOICES, default='general')
    content    = models.TextField()
    image_url  = models.URLField(blank=True, null=True)
    is_public  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.email} — {self.get_post_type_display()}'


class SocialComment(models.Model):
    post       = models.ForeignKey(SocialPost, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_comments')
    body       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.email} → Post #{self.post_id}'


class SocialReaction(models.Model):
    REACTION_CHOICES = [
        ('like',    '👍'),
        ('love',    '❤️'),
        ('clap',    '👏'),
        ('fire',    '🔥'),
        ('star',    '⭐'),
    ]
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_reactions')
    post       = models.ForeignKey(SocialPost, on_delete=models.CASCADE, related_name='reactions')
    reaction   = models.CharField(max_length=10, choices=REACTION_CHOICES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} → {self.reaction}'
