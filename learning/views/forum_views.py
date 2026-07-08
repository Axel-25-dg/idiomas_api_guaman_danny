"""
Vistas para el Módulo de Comunidad (Foro)
==========================================
ForumCategory  → GET/POST /api/forum-categories/
ForumThread    → GET/POST /api/forum-threads/
ForumPost      → GET/POST /api/forum-posts/
ForumReaction  → POST     /api/forum-reactions/
ForumReport    → POST     /api/forum-reports/
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from learning.models import (
    ForumCategory, ForumThread, ForumPost, ForumReaction, ForumReport,
)
from learning.serializers.forum_serializer import (
    ForumCategorySerializer, ForumThreadSerializer,
    ForumPostSerializer, ForumReactionSerializer, ForumReportSerializer,
)
from learning.permissions import IsAdminOrReadOnly, _get_role, ROLE_ADMIN
from learning.pagination import StandardPagination


class ForumCategoryViewSet(viewsets.ModelViewSet):
    """
    GET    /api/forum-categories/       — Listar categorías activas
    POST   /api/forum-categories/       — Crear categoría (admin)
    PUT    /api/forum-categories/{id}/  — Actualizar (admin)
    DELETE /api/forum-categories/{id}/  — Eliminar (admin)
    """
    queryset           = ForumCategory.objects.filter(is_active=True)
    serializer_class   = ForumCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [SearchFilter, OrderingFilter]
    search_fields      = ['name', 'description']
    ordering_fields    = ['order', 'name', 'created_at']


class ForumThreadViewSet(viewsets.ModelViewSet):
    """
    GET    /api/forum-threads/       — Listar hilos
    POST   /api/forum-threads/       — Crear hilo (autenticado)
    GET    /api/forum-threads/{id}/  — Detalle (incrementa vistas)
    PUT    /api/forum-threads/{id}/  — Editar (autor o admin)
    DELETE /api/forum-threads/{id}/  — Eliminar (admin)
    POST   /api/forum-threads/{id}/pin/   — Fijar hilo (admin)
    POST   /api/forum-threads/{id}/close/ — Cerrar hilo (admin)
    """
    queryset           = ForumThread.objects.select_related('category', 'author').all()
    serializer_class   = ForumThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['category', 'is_pinned', 'is_closed', 'author']
    search_fields      = ['title', 'body']
    ordering_fields    = ['created_at', 'views', 'is_pinned']

    def get_permissions(self):
        if self.action in ('destroy', 'pin', 'close'):
            from rest_framework.permissions import IsAuthenticated
            return [IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        thread = self.get_object()
        role = _get_role(request.user)
        if thread.author != request.user and role != ROLE_ADMIN:
            return Response(
                {'detail': 'Solo el autor o un admin puede editar este hilo.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        thread = self.get_object()
        role = _get_role(request.user)
        if thread.author != request.user and role != ROLE_ADMIN:
            return Response(
                {'detail': 'Solo el autor o un admin puede eliminar este hilo.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='pin')
    def pin(self, request, pk=None):
        """POST /api/forum-threads/{id}/pin/ — Fijar/desfijar (admin)"""
        role = _get_role(request.user)
        if role != ROLE_ADMIN:
            return Response({'detail': 'Solo admin puede fijar hilos.'}, status=status.HTTP_403_FORBIDDEN)
        thread = self.get_object()
        thread.is_pinned = not thread.is_pinned
        thread.save(update_fields=['is_pinned'])
        return Response({'is_pinned': thread.is_pinned})

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        """POST /api/forum-threads/{id}/close/ — Cerrar/abrir (admin)"""
        role = _get_role(request.user)
        if role != ROLE_ADMIN:
            return Response({'detail': 'Solo admin puede cerrar hilos.'}, status=status.HTTP_403_FORBIDDEN)
        thread = self.get_object()
        thread.is_closed = not thread.is_closed
        thread.save(update_fields=['is_closed'])
        return Response({'is_closed': thread.is_closed})


class ForumPostViewSet(viewsets.ModelViewSet):
    """
    GET    /api/forum-posts/       — Listar posts (filtrar por thread)
    POST   /api/forum-posts/       — Crear post
    PUT    /api/forum-posts/{id}/  — Editar (autor o admin)
    DELETE /api/forum-posts/{id}/  — Soft-delete (marca is_deleted=True)
    """
    queryset           = ForumPost.objects.filter(is_deleted=False).select_related('thread', 'author', 'parent')
    serializer_class   = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['thread', 'author', 'parent']
    search_fields      = ['body']
    ordering_fields    = ['created_at']

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        role = _get_role(request.user)
        if post.author != request.user and role != ROLE_ADMIN:
            return Response(
                {'detail': 'Solo el autor o un admin puede editar este post.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        role = _get_role(request.user)
        if post.author != request.user and role != ROLE_ADMIN:
            return Response(
                {'detail': 'Solo el autor o un admin puede eliminar este post.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        post.is_deleted = True
        post.save(update_fields=['is_deleted'])
        return Response({'detail': 'Post eliminado.'}, status=status.HTTP_200_OK)


class ForumReactionViewSet(viewsets.ModelViewSet):
    """
    GET    /api/forum-reactions/       — Mis reacciones
    POST   /api/forum-reactions/       — Reaccionar a un post
    DELETE /api/forum-reactions/{id}/  — Quitar reacción
    """
    serializer_class   = ForumReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ForumReaction.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Si ya existe, actualizar; si no, crear
        post_id  = request.data.get('post')
        reaction = request.data.get('reaction', 'like')
        existing = ForumReaction.objects.filter(user=request.user, post_id=post_id).first()
        if existing:
            existing.reaction = reaction
            existing.save(update_fields=['reaction'])
            return Response(ForumReactionSerializer(existing).data)
        return super().create(request, *args, **kwargs)


class ForumReportViewSet(viewsets.ModelViewSet):
    """
    GET    /api/forum-reports/       — Reportes (admin: todos, usuario: los suyos)
    POST   /api/forum-reports/       — Crear reporte
    PATCH  /api/forum-reports/{id}/  — Cambiar estado (admin)
    """
    serializer_class   = ForumReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['status']

    def get_queryset(self):
        role = _get_role(self.request.user)
        if role == ROLE_ADMIN:
            return ForumReport.objects.select_related('reporter', 'post').all()
        return ForumReport.objects.filter(reporter=self.request.user)
