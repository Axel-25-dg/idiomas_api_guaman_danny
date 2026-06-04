from django.db import models
from django.conf import settings


PAYMENT_STATUS_CHOICES = [
    ('approved', 'Aprobado'),
    ('rejected', 'Rechazado'),
    ('pending', 'Pendiente'),
]

PAYMENT_METHOD_CHOICES = [
    ('credit_card', 'Tarjeta de crédito'),
    ('debit_card', 'Tarjeta de débito'),
    ('paypal', 'PayPal'),
    ('transfer', 'Transferencia'),
]


class Subscription(models.Model):
    name = models.CharField(max_length=100)          # Ej: "Premium Mensual"
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    features = models.TextField(blank=True)          # JSON o texto con los beneficios

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f'{self.name} - ${self.price}'


class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='user_subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.user.email} - {self.subscription.name}'


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f'{self.user.email} - ${self.amount} ({self.status})'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - ${self.total_amount} ({self.status})'