from rest_framework import serializers
from learning.models import Order


class OrderSerializer(serializers.ModelSerializer):
    user_id           = serializers.IntegerField(source='user.id', read_only=True)
    user_email        = serializers.EmailField(source='user.email', read_only=True)
    subscription_name = serializers.CharField(source='subscription.name', read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id',
            'user_id', 'user_email',
            'subscription', 'subscription_name',
            'total_amount', 'payment_method',
            'status', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user_id', 'user_email', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Si no llega total_amount, se toma del precio del plan."""
        plan = attrs.get('subscription')
        if plan and not attrs.get('total_amount'):
            attrs['total_amount'] = plan.price
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if not validated_data.get('total_amount') and validated_data.get('subscription'):
            validated_data['total_amount'] = validated_data['subscription'].price
        return super().create(validated_data)
