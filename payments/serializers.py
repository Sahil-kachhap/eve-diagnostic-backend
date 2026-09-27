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

class PaymentWebhookSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=150)
    event_type = serializers.ChoiceField(
        choices=[
            "payment.success",
            "payment.failed",
        ]
    )
    provider_payment_id = serializers.CharField(
        max_length=100,
    )
    status = serializers.ChoiceField(
        choices=[
            "SUCCESS",
            "FAILED",
        ]
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )