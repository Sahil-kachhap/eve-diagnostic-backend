from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Booking
from .serializers import (
    BookingSerializer,
    CreateBookingSerializer,
)
from .services import cancel_booking, create_booking

class BookingCreateView(generics.CreateAPIView):
    serializer_class = CreateBookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = create_booking(
            user=request.user,
            centre_test_id=serializer.validated_data["centre_test"].id,
            appointment_at=serializer.validated_data["appointment_at"],
        )

        return Response(
            BookingSerializer(booking).data,
            status=201,
        )

class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects
            .filter(user=self.request.user)
            .select_related(
                "centre_test__centre",
                "centre_test__test",
            )
            .order_by("-created_at")
        )

class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateBookingSerializer
        return BookingSerializer

    def get_queryset(self):
        return (
            Booking.objects
            .filter(user=self.request.user)
            .select_related(
                "centre_test__centre",
                "centre_test__test",
            )
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = create_booking(
            user=request.user,
            centre_test_id=serializer.validated_data["centre_test"].id,
            appointment_at=serializer.validated_data["appointment_at"],
        )

        return Response(
            BookingSerializer(booking).data,
            status=201,
        )

class BookingDetailView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects
            .filter(user=self.request.user)
            .select_related(
                "centre_test__centre",
                "centre_test__test",
            )
        )

class BookingCancelView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        booking = cancel_booking(
            user=request.user,
            booking_id=pk,
        )

        return Response(
            BookingSerializer(booking).data,
            status=200,
        )