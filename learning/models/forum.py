"""
Módulo de Foro de Comunidad
===========================
ForumCategory  → categoría del foro
ForumThread    → hilo de discusión
ForumPost      → respuesta/comentario
ForumReaction  → reacción (like, etc.)
ForumReport    → reporte de contenido
"""
from django.db import models
from django.conf import settings


class ForumCategory(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=50, blank=True, help_text='Nombre del ícono o emoji')
    order       = models.PositiveIntegerField(default=1)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ForumThread(models.Model):
    category   = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='threads')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_threads')
    title      = models.CharField(max_length=200)
    body       = models.TextField()
    is_pinned  = models.BooleanField(default=False)
    is_closed  = models.BooleanField(default=False)
    views      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f'{self.title} — {self.author.email}'


class ForumPost(models.Model):
    thread     = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    parent     = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    body       = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Post de {self.author.email} en "{self.thread.title}"'


class ForumReaction(models.Model):
    REACTION_CHOICES = [
        ('like',     '👍'),
        ('love',     '❤️'),
        ('helpful',  '💡'),
        ('confused', '❓'),
    ]
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_reactions')
    post       = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='reactions')
    reaction   = models.CharField(max_length=10, choices=REACTION_CHOICES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} → {self.reaction} en Post #{self.post_id}'


class ForumReport(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pendiente'),
        ('reviewed', 'Revisado'),
        ('resolved', 'Resuelto'),
    ]
    reporter   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_reports')
    post       = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='reports')
    reason     = models.TextField()
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Reporte de {self.reporter.email} sobre Post #{self.post_id}'
