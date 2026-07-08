"""
Vistas para el Módulo de Comunicación
======================================
MessageThread  → GET/POST /api/threads/
Message        → GET/POST /api/threads/{id}/messages/
                 POST     /api/messages/{id}/read/
"""
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from learning.models import MessageThread, Message, MessageAttachment
from learning.serializers.messaging_serializer import (
    MessageThreadSerializer, MessageSerializer, MessageAttachmentSerializer,
)
from learning.pagination import StandardPagination


class MessageThreadViewSet(viewsets.ModelViewSet):
    """
    GET    /api/threads/          — Hilos del usuario autenticado
    POST   /api/threads/          — Crear hilo nuevo
    GET    /api/threads/{id}/     — Detalle del hilo
    DELETE /api/threads/{id}/     — Desactivar hilo
    GET    /api/threads/{id}/messages/  — Mensajes del hilo
    POST   /api/threads/{id}/messages/  — Enviar mensaje al hilo
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = MessageThreadSerializer
    pagination_class   = StandardPagination
    http_method_names  = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return MessageThread.objects.filter(
            participants=self.request.user,
            is_active=True,
        ).prefetch_related('participants', 'messages').distinct()

    def perform_create(self, serializer):
        thread = serializer.save()
        # Asegurar que el creador sea participante
        thread.participants.add(self.request.user)

    def destroy(self, request, *args, **kwargs):
        thread = self.get_object()
        thread.is_active = False
        thread.save(update_fields=['is_active'])
        return Response({'detail': 'Hilo desactivado.'}, status=status.HTTP_200_OK)

    # ── Mensajes dentro del hilo ─────────────────────────────────────────────
    @action(detail=True, methods=['get', 'post'], url_path='messages')
    def messages(self, request, pk=None):
        """
        GET  /api/threads/{id}/messages/ — Lista paginada de mensajes
        POST /api/threads/{id}/messages/ — Enviar un mensaje al hilo
        """
        thread = self.get_object()

        if request.method == 'GET':
            qs = thread.messages.select_related('sender').prefetch_related('attachments')
            page = self.paginate_queryset(qs)
            serializer = MessageSerializer(
                page if page is not None else qs,
                many=True,
                context={'request': request},
            )
            # Marcar como leídos los mensajes de otros usuarios
            thread.messages.exclude(sender=request.user).filter(
                is_read=False
            ).update(is_read=True, read_at=timezone.now())

            if page is not None:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.data)

        # POST — enviar mensaje
        serializer = MessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user, thread=thread)
        # Actualizar timestamp del hilo
        thread.save(update_fields=['updated_at'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.GenericViewSet):
    """
    POST /api/messages/{id}/read/ — Marcar mensaje como leído
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(thread__participants=self.request.user)

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        msg = self.get_object()
        if msg.sender != request.user and not msg.is_read:
            msg.is_read = True
            msg.read_at = timezone.now()
            msg.save(update_fields=['is_read', 'read_at'])
        return Response({'detail': 'Mensaje marcado como leído.'})
