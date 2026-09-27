from django.utils import timezone
from rest_framework import serializers
from catalogue.models import CentreTest
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    centre_name = serializers.CharField(
        source="centre_test.centre.name",
        read_only=True,
    )
    test_name = serializers.CharField(
        source="centre_test.test.name",
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "centre_test",
            "centre_name",
            "test_name",
            "appointment_at",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "centre_name",
            "test_name",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_centre_test(self, value):
        if not value.is_available:
            raise serializers.ValidationError(
                "This test is currently unavailable."
            )
        return value

    def validate_appointment_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Appointment time must be in the future."
            )
        return value

class CreateBookingSerializer(serializers.Serializer):
    centre_test = serializers.PrimaryKeyRelatedField(
        queryset=CentreTest.objects.all()
    )
    appointment_at = serializers.DateTimeField()

    def validate_centre_test(self, value):
        if not value.is_available:
            raise serializers.ValidationError(
                "This test is currently unavailable."
            )
        return value