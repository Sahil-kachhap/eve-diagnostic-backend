import pytest
from rest_framework.test import APIClient

from accounts.models import User
from catalogue.models import DiagnosticCentre


@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        name="Normal User",
        password="password123",
    )


@pytest.fixture
def admin():
    return User.objects.create_user(
        email="admin@example.com",
        name="Admin",
        password="password123",
        role=User.Role.ADMIN,
        is_staff=True,
    )

@pytest.mark.django_db
def test_normal_user_cannot_create_centre(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/catalogue/centres/",
        {
            "name": "Apollo",
            "location": "Delhi",
        },
        format="json",
    )

    assert response.status_code == 403

@pytest.mark.django_db
def test_admin_can_create_centre(admin):
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        "/api/v1/catalogue/centres/",
        {
            "name": "Apollo",
            "location": "Delhi",
        },
        format="json",
    )

    assert response.status_code == 201

@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_bookings():
    client = APIClient()

    response = client.get(
        "/api/v1/bookings/"
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_user_cannot_access_other_users_booking(
    user,
):
    from datetime import timedelta
    from django.utils import timezone
    from bookings.models import Booking
    from catalogue.models import (
        CentreTest,
        DiagnosticCentre,
        DiagnosticTest,
    )

    other_user = User.objects.create_user(
        email="other@example.com",
        name="Other User",
        password="password123",
    )

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
    )

    booking = Booking.objects.create(
        user=other_user,
        centre_test=centre_test,
        appointment_at=timezone.now() + timedelta(days=1),
        amount="500.00",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(
        f"/api/v1/bookings/{booking.id}/"
    )

    assert response.status_code == 404

