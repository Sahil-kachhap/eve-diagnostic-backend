from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import (
    CreatePaymentSerializer,
    PaymentSerializer,
    PaymentWebhookSerializer
)
from django.conf import settings
from rest_framework.views import APIView

from .services import (
    create_payment,
    process_payment_webhook,
    validate_webhook_signature,
)

import json

class PaymentCreateView(generics.GenericAPIView):
    serializer_class = CreatePaymentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        payment = create_payment(
            user=request.user,
            booking_id=serializer.validated_data[
                "booking_id"
            ],
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )

class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        signature = request.headers.get(
            "X-Webhook-Signature"
        )

        if not signature:
            return Response(
                {"detail": "Missing webhook signature."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not validate_webhook_signature(
            payload=request.body,
            signature=signature,
        ):
            return Response(
                {"detail": "Invalid webhook signature."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = json.loads(
                request.body.decode("utf-8")
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response(
                {"detail": "Invalid JSON payload."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PaymentWebhookSerializer(
            data=payload
        )
        serializer.is_valid(raise_exception=True)

        payment = process_payment_webhook(
            event_id=serializer.validated_data["event_id"],
            event_type=serializer.validated_data["event_type"],
            provider_payment_id=serializer.validated_data[
                "provider_payment_id"
            ],
            status=serializer.validated_data["status"],
            amount=serializer.validated_data["amount"],
            payload=payload,
        )

        return Response(
            {
                "detail": "Webhook processed successfully.",
                "payment_id": payment.id,
                "status": payment.status,
            },
            status=status.HTTP_200_OK,
        )