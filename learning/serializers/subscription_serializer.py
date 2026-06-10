from datetime import date, timedelta
from rest_framework import serializers
from learning.models import Subscription, UserSubscription, Payment


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'name', 'price', 'duration_days', 'features']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value


class UserSubscriptionSerializer(serializers.ModelSerializer):
    subscription_name = serializers.CharField(source='subscription.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'user_email', 'subscription', 'subscription_name',
                  'start_date', 'end_date', 'is_active']
        read_only_fields = ['user', 'start_date', 'end_date']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Calcular fechas automáticamente en el servidor
        subscription_plan = validated_data['subscription']
        validated_data['start_date'] = date.today()
        validated_data['end_date'] = date.today() + timedelta(days=subscription_plan.duration_days)
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_email', 'amount', 'payment_method', 'transaction_date', 'status']
        read_only_fields = ['user', 'transaction_date']

    def create(self, validated_data):
        from learning.services.email_service import send_payment_confirmation
        validated_data['user'] = self.context['request'].user
        instance = super().create(validated_data)
        
        # Enviar correo de confirmación
        if instance.status == 'approved':
            try:
                send_payment_confirmation(instance.user, instance)
            except Exception:
                pass
        return instance
