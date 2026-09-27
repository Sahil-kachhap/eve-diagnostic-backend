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


@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        name="Test User",
        password="password123",
    )


@pytest.fixture
def centre_test():
    centre = DiagnosticCentre.objects.create(
        name="Apollo",
        location="Delhi",
    )

    test = DiagnosticTest.objects.create(
        name="Blood Test",
    )

    return CentreTest.objects.create(
        centre=centre,
        test=test,
        price="500.00",
        is_available=True,
    )


@pytest.mark.django_db
def test_create_booking(user, centre_test):
    client = APIClient()
    client.force_authenticate(user=user)

    appointment = timezone.now() + timedelta(days=1)

    response = client.post(
        "/api/v1/bookings/",
        {
            "centre_test": centre_test.id,
            "appointment_at": appointment.isoformat(),
        },
        format="json",
    )

    assert response.status_code == 201

    booking = Booking.objects.get()

    assert booking.user == user
    assert Decimal(booking.amount) == Decimal(centre_test.price)
    assert booking.status == Booking.Status.PENDING


@pytest.mark.django_db
def test_booking_snapshots_price(user, centre_test):
    client = APIClient()
    client.force_authenticate(user=user)

    appointment = timezone.now() + timedelta(days=1)

    response = client.post(
        "/api/v1/bookings/",
        {
            "centre_test": centre_test.id,
            "appointment_at": appointment.isoformat(),
        },
        format="json",
    )

    assert response.status_code == 201

    booking = Booking.objects.get()

    centre_test.price = "800.00"
    centre_test.save()

    booking.refresh_from_db()

    assert booking.amount == 500

@pytest.mark.django_db
def test_user_only_sees_own_bookings(user, centre_test):
    other_user = User.objects.create_user(
        email="other@example.com",
        name="Other User",
        password="password123",
    )

    Booking.objects.create(
        user=user,
        centre_test=centre_test,
        appointment_at=timezone.now() + timedelta(days=1),
        amount=centre_test.price,
    )

    Booking.objects.create(
        user=other_user,
        centre_test=centre_test,
        appointment_at=timezone.now() + timedelta(days=2),
        amount=centre_test.price,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/bookings/")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1

@pytest.mark.django_db
def test_pending_booking_can_be_cancelled(user, centre_test):
    booking = Booking.objects.create(
        user=user,
        centre_test=centre_test,
        appointment_at=timezone.now() + timedelta(days=1),
        amount=centre_test.price,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        f"/api/v1/bookings/{booking.id}/cancel/"
    )

    assert response.status_code == 200

    booking.refresh_from_db()

    assert booking.status == Booking.Status.CANCELLED

