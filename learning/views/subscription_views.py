from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from learning.models import Subscription, UserSubscription, Payment
from learning.serializers import SubscriptionSerializer, UserSubscriptionSerializer, PaymentSerializer
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
