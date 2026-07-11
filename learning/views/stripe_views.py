"""
Stripe Payment Views
====================
Dos endpoints:

1. POST /api/stripe/create-payment-intent/
   Flutter llama esto para obtener el clientSecret y mostrar la hoja de pago.

2. POST /api/stripe/webhook/
   Stripe llama esto automáticamente cuando el pago se confirma.
   Activa la suscripción del usuario.

Requiere en .env:
  STRIPE_SECRET_KEY=sk_test_...
  STRIPE_PUBLISHABLE_KEY=pk_test_...
  STRIPE_WEBHOOK_SECRET=whsec_...
"""
import json
import stripe
import logging

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from learning.models import Subscription, Order, UserSubscription
from learning.serializers import OrderSerializer

logger = logging.getLogger(__name__)


def _get_stripe():
    """Inicializa stripe con la clave del settings en tiempo de ejecución, no de importación."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


class CreatePaymentIntentView(APIView):
    """
    POST /api/stripe/create-payment-intent/

    Body:
      { "subscription_id": 2, "payment_method": "credit_card" }

    Respuesta:
      {
        "client_secret": "pi_xxx_secret_xxx",
        "order_id": 15,
        "amount": 1999,          ← centavos (USD)
        "currency": "usd",
        "publishable_key": "pk_test_..."
      }

    Flutter usa client_secret con flutter_stripe para mostrar el Sheet de pago.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes     = [permissions.IsAuthenticated]

    def post(self, request):
        subscription_id = request.data.get('subscription_id')
        payment_method  = request.data.get('payment_method', 'credit_card')

        if not subscription_id:
            return Response(
                {'detail': 'subscription_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            plan = Subscription.objects.get(pk=subscription_id, is_active=True)
        except Subscription.DoesNotExist:
            return Response(
                {'detail': 'Plan no encontrado o inactivo.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {'detail': 'Stripe no está configurado en el servidor.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Crear orden interna (status: pending)
        order = Order.objects.create(
            user=request.user,
            subscription=plan,
            total_amount=plan.price,
            payment_method=payment_method,
            status='pending',
        )

        # Crear PaymentIntent en Stripe
        # amount en centavos: $19.99 → 1999
        amount_cents = int(plan.price * 100)

        _stripe = _get_stripe()
        intent = _stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={
                'order_id':    order.id,
                'user_id':     request.user.id,
                'user_email':  request.user.email,
                'plan_name':   plan.name,
            },
            description=f'JumpUp — Plan {plan.name} ({plan.duration_days} días)',
        )

        # Guardar referencia del PaymentIntent en la orden
        order.notes = intent.id
        order.save(update_fields=['notes'])

        return Response({
            'client_secret':   intent.client_secret,
            'order_id':        order.id,
            'amount':          amount_cents,
            'currency':        'usd',
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    POST /api/stripe/webhook/

    Stripe envía eventos aquí cuando ocurre algo con el pago.
    El único evento que interesa es payment_intent.succeeded:
    cuando el pago es exitoso, se aprueba la orden y se activa la suscripción.

    En el dashboard de Stripe configura el webhook apuntando a:
      https://guaman-idiomas-ute.online/api/stripe/webhook/

    Eventos a suscribir:
      - payment_intent.succeeded
      - payment_intent.payment_failed  (opcional, para logs)
    """
    authentication_classes = []
    permission_classes     = [permissions.AllowAny]

    def post(self, request):
        payload    = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        if not settings.STRIPE_WEBHOOK_SECRET:
            # Sin secret configurado, modo desarrollo: confiar en el payload
            try:
                event = stripe.Event.construct_from(
                    json.loads(payload), stripe.api_key
                )
            except Exception as e:
                logger.error(f'Stripe webhook parse error: {e}')
                return Response({'detail': 'Invalid payload.'}, status=400)
        else:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
            except stripe.error.SignatureVerificationError as e:
                logger.warning(f'Stripe signature invalid: {e}')
                return Response({'detail': 'Invalid signature.'}, status=400)
            except Exception as e:
                logger.error(f'Stripe webhook error: {e}')
                return Response({'detail': 'Webhook error.'}, status=400)

        # ── Pago exitoso ──────────────────────────────────────────────────────
        if event['type'] == 'payment_intent.succeeded':
            intent   = event['data']['object']
            order_id = intent.get('metadata', {}).get('order_id')

            if order_id:
                try:
                    order = Order.objects.get(pk=order_id, status='pending')
                    order.status = 'approved'
                    order.save(update_fields=['status', 'updated_at'])

                    # La señal on_order_approved activa UserSubscription automáticamente
                    logger.info(
                        f'Stripe: orden #{order_id} aprobada para usuario {order.user.email}'
                    )
                except Order.DoesNotExist:
                    logger.warning(f'Stripe webhook: orden #{order_id} no encontrada o ya aprobada.')

        # ── Pago fallido ──────────────────────────────────────────────────────
        elif event['type'] == 'payment_intent.payment_failed':
            intent   = event['data']['object']
            order_id = intent.get('metadata', {}).get('order_id')
            reason   = intent.get('last_payment_error', {}).get('message', 'desconocido')
            logger.warning(f'Stripe: pago fallido en orden #{order_id} — {reason}')

            if order_id:
                Order.objects.filter(pk=order_id, status='pending').update(
                    status='rejected',
                    notes=f'Fallo Stripe: {reason}',
                )

        return Response({'received': True})
