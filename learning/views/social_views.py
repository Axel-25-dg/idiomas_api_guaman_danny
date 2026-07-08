"""
Vistas para el Feed Social
===========================
SocialPost     → GET/POST /api/social-posts/
SocialComment  → GET/POST /api/social-comments/
SocialReaction → GET/POST /api/social-reactions/
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from learning.models import SocialPost, SocialComment, SocialReaction
from learning.serializers.social_serializer import (
    SocialPostSerializer, SocialCommentSerializer, SocialReactionSerializer,
)
from learning.permissions import _get_role, ROLE_ADMIN
from learning.pagination import StandardPagination


class SocialPostViewSet(viewsets.ModelViewSet):
    """
    GET    /api/social-posts/        — Feed público (o privado del usuario)
    POST   /api/social-posts/        — Crear publicación
    GET    /api/social-posts/{id}/   — Detalle con comentarios
    PUT    /api/social-posts/{id}/   — Editar (autor o admin)
    DELETE /api/social-posts/{id}/   — Eliminar (autor o admin)
    GET    /api/social-posts/mine/   — Solo mis publicaciones
    """
    serializer_class   = SocialPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['post_type', 'is_public', 'author']
    search_fields      = ['content']
    ordering_fields    = ['created_at']

    def get_queryset(self):
        # Feed: publicaciones públicas o del propio usuario
        user = self.request.user
        return SocialPost.objects.filter(
            is_public=True
        ).select_related('author').prefetch_related('comments', 'reactions') | \
        SocialPost.objects.filter(
            author=user
        ).select_related('author').prefetch_related('comments', 'reactions')

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        role = _get_role(request.user)
        if post.author != request.user and role != ROLE_ADMIN:
            return Response(
                {'detail': 'Solo el autor o un admin puede editar esta publicación.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        role = _get_role(request.user)
        if post.author != request.user and role != ROLE_ADMIN:
            return Response(
                {'detail': 'Solo el autor o un admin puede eliminar esta publicación.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='mine')
    def mine(self, request):
        """GET /api/social-posts/mine/ — Solo las publicaciones del usuario autenticado"""
        qs = SocialPost.objects.filter(author=request.user).order_by('-created_at')
        page = self.paginate_queryset(qs)
        serializer = SocialPostSerializer(
            page if page is not None else qs,
            many=True, context={'request': request},
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class SocialCommentViewSet(viewsets.ModelViewSet):
    """
    GET    /api/social-comments/       — Comentarios (filtrar por post)
    POST   /api/social-comments/       — Comentar
    DELETE /api/social-comments/{id}/  — Eliminar (autor o admin)
    """
    serializer_class   = SocialCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['post']

    def get_queryset(self):
        return SocialComment.objects.select_related('author', 'post').all()

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        role = _get_role(request.user)
        if comment.author != request.user and role != ROLE_ADMIN:
            return Response(
                {'detail': 'Solo el autor o un admin puede eliminar este comentario.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class SocialReactionViewSet(viewsets.ModelViewSet):
    """
    GET    /api/social-reactions/       — Mis reacciones
    POST   /api/social-reactions/       — Reaccionar a un post (upsert)
    DELETE /api/social-reactions/{id}/  — Quitar reacción
    """
    serializer_class   = SocialReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SocialReaction.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Upsert: si ya existe una reacción del user en ese post, actualizar
        post_id  = request.data.get('post')
        reaction = request.data.get('reaction', 'like')
        existing = SocialReaction.objects.filter(user=request.user, post_id=post_id).first()
        if existing:
            existing.reaction = reaction
            existing.save(update_fields=['reaction'])
            return Response(SocialReactionSerializer(existing).data)
        return super().create(request, *args, **kwargs)
