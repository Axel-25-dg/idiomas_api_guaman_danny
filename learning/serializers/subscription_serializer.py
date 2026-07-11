from datetime import date, timedelta
from rest_framework import serializers
from learning.models import Subscription, UserSubscription, Payment


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Subscription
        fields = ['id', 'name', 'price', 'duration_days', 'features', 'max_languages', 'is_active', 'created_at']
        read_only_fields = ['created_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value


class UserSubscriptionSerializer(serializers.ModelSerializer):
    subscription_name   = serializers.CharField(source='subscription.name', read_only=True)
    subscription_price  = serializers.DecimalField(source='subscription.price', max_digits=8, decimal_places=2, read_only=True)
    subscription_features = serializers.CharField(source='subscription.features', read_only=True)
    max_languages       = serializers.IntegerField(source='subscription.max_languages', read_only=True)
    user_email          = serializers.EmailField(source='user.email', read_only=True)
    is_currently_valid  = serializers.BooleanField(read_only=True)

    class Meta:
        model  = UserSubscription
        fields = [
            'id', 'user', 'user_email',
            'subscription', 'subscription_name', 'subscription_price',
            'subscription_features', 'max_languages',
            'start_date', 'end_date', 'is_active', 'is_currently_valid',
        ]
        read_only_fields = ['user', 'start_date', 'end_date', 'is_currently_valid']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        plan = validated_data['subscription']
        validated_data['start_date'] = date.today()
        validated_data['end_date']   = date.today() + timedelta(days=plan.duration_days)
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model  = Payment
        fields = [
            'id', 'user', 'user_email', 'order',
            'amount', 'payment_method', 'transaction_date', 'status', 'reference',
        ]
        read_only_fields = ['user', 'transaction_date']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        instance = super().create(validated_data)
        if instance.status == 'approved':
            try:
                from learning.services.email_service import send_payment_confirmation
                send_payment_confirmation(instance.user, instance)
            except Exception:
                pass
        return instance
