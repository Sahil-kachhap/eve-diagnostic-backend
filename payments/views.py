from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    CreatePaymentSerializer,
    PaymentSerializer,
)
from .services import create_payment


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