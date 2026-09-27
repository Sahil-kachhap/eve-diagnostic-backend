from rest_framework import serializers
from .models import Payment


class CreatePaymentSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "provider_payment_id",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields