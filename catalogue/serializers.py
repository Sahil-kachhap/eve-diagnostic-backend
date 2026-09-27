from rest_framework import serializers
from .models import DiagnosticCentre, DiagnosticTest, CentreTest


class DiagnosticCentreSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticCentre
        fields = [
            "id",
            "name",
            "location",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class DiagnosticTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticTest
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class CentreTestSerializer(serializers.ModelSerializer):
    centre_name = serializers.CharField(
        source="centre.name",
        read_only=True,
    )
    test_name = serializers.CharField(
        source="test.name",
        read_only=True,
    )

    class Meta:
        model = CentreTest
        fields = [
            "id",
            "centre",
            "centre_name",
            "test",
            "test_name",
            "price",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "centre_name",
            "test_name",
            "created_at",
            "updated_at",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )
        return value