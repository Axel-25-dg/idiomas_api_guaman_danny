from rest_framework import serializers
from learning.models import Order


class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    def create(self, validated_data):
        from learning.services.email_service import send_payment_confirmation
        instance = super().create(validated_data)
        
        # Enviar correo si la orden se crea aprobada (o podrías hacerlo al actualizar status)
        if instance.status == 'approved':
            try:
                send_payment_confirmation(instance.user, instance)
            except Exception:
                pass
        return instance

    class Meta:
        model = Order
        fields = [
            'id',
            'user_id',
            'user_email',
            'subscription',
            'total_amount',
            'payment_method',
            'status',
            'created_at',
            'notes',
        ]
        read_only_fields = ['id', 'user_id', 'user_email', 'created_at']
