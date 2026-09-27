from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from bookings.models import Booking
from catalogue.models import (
    CentreTest,
    DiagnosticCentre,
    DiagnosticTest,
)
from payments.models import Payment


@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        name="Test User",
        password="password123",
    )


@pytest.fixture
def booking(user):
    centre = DiagnosticCentre.objects.create(
        name="Apollo",
        location="Delhi",
    )

    test = DiagnosticTest.objects.create(
        name="Blood Test",
    )

    centre_test = CentreTest.objects.create(
        centre=centre,
        test=test,
        price="500.00",
        is_available=True,
    )

    return Booking.objects.create(
        user=user,
        centre_test=centre_test,
        appointment_at=timezone.now() + timedelta(days=1),
        amount="500.00",
        status=Booking.Status.PENDING,
    )


@pytest.mark.django_db
def test_create_payment(user, booking):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/payments/",
        {
            "booking_id": booking.id,
        },
        format="json",
    )

    assert response.status_code == 201

    payment = Payment.objects.get()

    assert payment.booking == booking
    assert Decimal(payment.amount) == Decimal(booking.amount)
    assert payment.status == Payment.Status.PENDING
    assert payment.provider_payment_id.startswith("mock_")

@pytest.mark.django_db
def test_duplicate_payment_returns_existing_payment(
    user,
    booking,
):
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post(
        "/api/v1/payments/",
        {"booking_id": booking.id},
        format="json",
    )

    second = client.post(
        "/api/v1/payments/",
        {"booking_id": booking.id},
        format="json",
    )

    assert first.data["id"] == second.data["id"]
    assert Payment.objects.filter(
        booking=booking
    ).count() == 1

