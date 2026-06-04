from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from learning.models import Subscription, UserSubscription, Payment, Order
from learning.serializers import (
    SubscriptionSerializer, UserSubscriptionSerializer, PaymentSerializer, OrderSerializer
)
from learning.pagination import StandardPagination
from learning.permissions import IsAdminOrReadOnly


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    GET    /api/subscriptions/        — Lista los planes disponibles
    POST   /api/subscriptions/        — Crea un plan (solo admin)
    GET    /api/subscriptions/{id}/   — Detalle del plan
    PUT    /api/subscriptions/{id}/   — Actualiza (solo admin)
    DELETE /api/subscriptions/{id}/   — Elimina (solo admin)
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['price', 'duration_days']


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    GET  /api/my-subscriptions/       — Suscripciones activas del usuario
    POST /api/my-subscriptions/       — Suscribirse a un plan
    GET  /api/my-subscriptions/{id}/  — Detalle
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['start_date', 'end_date']

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user).select_related('subscription')


class PaymentViewSet(viewsets.ModelViewSet):
    """
    GET  /api/payments/       — Historial de pagos del usuario
    POST /api/payments/       — Registrar un pago
    GET  /api/payments/{id}/  — Detalle del pago
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_method']
    ordering_fields = ['transaction_date', 'amount']

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """
    GET    /api/orders/          — Lista órdenes del usuario o todas si es admin
    POST   /api/orders/          — Crea una orden para el usuario autenticado
    GET    /api/orders/{id}/     — Detalle de la orden
    GET    /api/orders/stats/    — Estadísticas de ventas (solo admin)
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'subscription']
    ordering_fields = ['created_at', 'total_amount']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.select_related('user', 'subscription').all()
        return Order.objects.filter(user=self.request.user).select_related('subscription')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        stats_data = Order.objects.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id')
        )

        return Response({
            'total_revenue': stats_data['total_revenue'] or 0.0,
            'total_orders': stats_data['total_orders'] or 0,
        }, status=status.HTTP_200_OK)
