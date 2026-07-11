from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from learning.models import Subscription, UserSubscription, Payment, Order
from learning.serializers import (
    SubscriptionSerializer, UserSubscriptionSerializer,
    PaymentSerializer, OrderSerializer,
)
from learning.pagination import StandardPagination
from learning.permissions import IsAdminOrReadOnly, IsAdmin


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    GET    /api/subscriptions/         — Lista de planes (autenticado)
    POST   /api/subscriptions/         — Solo admin
    PUT    /api/subscriptions/{id}/    — Solo admin
    DELETE /api/subscriptions/{id}/    — Solo admin
    GET    /api/subscriptions/active/  — Solo planes activos (útil para la tienda)
    """
    queryset           = Subscription.objects.all()
    serializer_class   = SubscriptionSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['is_active']
    ordering_fields    = ['price', 'duration_days']

    @action(detail=False, methods=['get'], url_path='active',
            permission_classes=[permissions.IsAuthenticated])
    def active(self, request):
        """GET /api/subscriptions/active/ — Solo planes activos para mostrar en tienda."""
        plans = Subscription.objects.filter(is_active=True).order_by('price')
        serializer = SubscriptionSerializer(plans, many=True)
        return Response(serializer.data)


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    GET    /api/my-subscriptions/              — Suscripciones del usuario autenticado
    POST   /api/my-subscriptions/              — Suscribirse a un plan (crea Order + activa)
    GET    /api/my-subscriptions/{id}/         — Detalle
    GET    /api/my-subscriptions/current/      — Suscripción activa actual
    GET    /api/my-subscriptions/language-limit/ — Cuántos idiomas puede aprender
    POST   /api/my-subscriptions/{id}/cancel/  — Cancelar suscripción activa
    """
    serializer_class   = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['is_active']
    ordering_fields    = ['start_date', 'end_date']

    def get_queryset(self):
        return UserSubscription.objects.filter(
            user=self.request.user
        ).select_related('subscription')

    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        """
        GET /api/my-subscriptions/current/
        Devuelve la suscripción activa y vigente del usuario,
        o null si no tiene ninguna.
        """
        today = timezone.now().date()
        sub = UserSubscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gte=today,
        ).select_related('subscription').order_by('-end_date').first()

        if sub:
            return Response(UserSubscriptionSerializer(sub).data)
        return Response({'detail': 'Sin suscripción activa.', 'subscription': None})

    @action(detail=False, methods=['get'], url_path='language-limit')
    def language_limit(self, request):
        """
        GET /api/my-subscriptions/language-limit/
        Devuelve cuántos idiomas puede aprender el usuario según su plan.
        0 = ilimitado.
        """
        today = timezone.now().date()
        sub = UserSubscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gte=today,
        ).select_related('subscription').order_by('-end_date').first()

        if sub:
            max_lang = sub.subscription.max_languages
        else:
            max_lang = 1  # plan gratuito: solo 1 idioma

        current_count = request.user.profile.languages_learning.count() \
            if hasattr(request.user, 'profile') else 0

        return Response({
            'max_languages':     max_lang,
            'current_languages': current_count,
            'is_premium':        sub is not None,
            'can_add_more':      max_lang == 0 or current_count < max_lang,
        })

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        POST /api/my-subscriptions/{id}/cancel/
        Cancela la suscripción del usuario autenticado.
        La suscripción queda inactiva pero los días pagados siguen corriendo
        hasta end_date (no se hace reembolso automático).
        """
        sub = self.get_object()

        if not sub.is_active:
            return Response(
                {'detail': 'Esta suscripción ya está cancelada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.now().date()
        if sub.end_date < today:
            return Response(
                {'detail': 'Esta suscripción ya expiró.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sub.is_active = False
        sub.save(update_fields=['is_active'])

        return Response({
            'detail': 'Suscripción cancelada. El acceso se mantiene hasta la fecha de vencimiento.',
            'end_date': sub.end_date.isoformat(),
            'subscription': UserSubscriptionSerializer(sub).data,
        })


class PaymentViewSet(viewsets.ModelViewSet):
    """
    GET  /api/payments/       — Historial de pagos del usuario autenticado
    POST /api/payments/       — Registrar un pago manualmente
    GET  /api/payments/{id}/  — Detalle del pago
    """
    serializer_class   = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['status', 'payment_method']
    ordering_fields    = ['transaction_date', 'amount']

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """
    GET    /api/orders/          — Propias del usuario; admin ve todas
    POST   /api/orders/          — Crear orden de pago
    GET    /api/orders/{id}/     — Detalle
    POST   /api/orders/{id}/approve/ — Aprobar orden (admin o simulación de webhook)
    GET    /api/orders/stats/    — Estadísticas de ventas (solo admin)
    """
    serializer_class   = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['status', 'payment_method', 'subscription']
    ordering_fields    = ['created_at', 'total_amount']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.select_related('user', 'subscription').all()
        return Order.objects.filter(
            user=self.request.user
        ).select_related('subscription')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='approve',
            permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        """
        POST /api/orders/{id}/approve/
        Aprueba una orden pendiente (solo admin / webhook).
        Al aprobar, el signal on_order_approved activa la suscripción automáticamente.
        """
        order = self.get_object()
        if order.status == 'approved':
            return Response({'detail': 'La orden ya estaba aprobada.'}, status=status.HTTP_200_OK)

        order.status = 'approved'
        order.save(update_fields=['status', 'updated_at'])

        return Response({
            'detail': 'Orden aprobada. Suscripción activada automáticamente.',
            'order':  OrderSerializer(order).data,
        })

    @action(detail=False, methods=['get'], url_path='stats',
            permission_classes=[IsAdmin])
    def stats(self, request):
        """GET /api/orders/stats/ — Estadísticas de ventas (solo admin)."""
        from django.db.models.functions import TruncMonth
        stats_data = Order.objects.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
            approved_orders=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(status='approved')),
        )
        monthly = (
            Order.objects.filter(status='approved')
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(revenue=Sum('total_amount'), count=Count('id'))
            .order_by('month')
        )
        return Response({
            'total_revenue':   stats_data['total_revenue'] or 0.0,
            'total_orders':    stats_data['total_orders']  or 0,
            'approved_orders': stats_data['approved_orders'] or 0,
            'monthly':         list(monthly),
        }, status=status.HTTP_200_OK)
