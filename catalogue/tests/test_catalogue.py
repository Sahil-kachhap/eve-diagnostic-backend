import pytest
from rest_framework.test import APIClient

from accounts.models import User
from catalogue.models import (
    CentreTest,
    DiagnosticCentre,
    DiagnosticTest,
)


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email="admin@example.com",
        name="Admin",
        password="password123",
        role=User.Role.ADMIN,
        is_staff=True,
    )


@pytest.fixture
def normal_user():
    return User.objects.create_user(
        email="user@example.com",
        name="User",
        password="password123",
    )


@pytest.mark.django_db
def test_admin_can_create_centre(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)

    response = client.post(
        "/api/v1/catalogue/centres/",
        {
            "name": "Apollo Diagnostics",
            "location": "Bangalore",
        },
        format="json",
    )

    assert response.status_code == 201
    assert DiagnosticCentre.objects.count() == 1


@pytest.mark.django_db
def test_user_can_list_centres(normal_user):
    DiagnosticCentre.objects.create(
        name="Apollo Diagnostics",
        location="Bangalore",
    )

    client = APIClient()
    client.force_authenticate(user=normal_user)

    response = client.get(
        "/api/v1/catalogue/centres/"
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_admin_can_create_test(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)

    response = client.post(
        "/api/v1/catalogue/tests/",
        {
            "name": "Blood Test",
            "description": "Complete blood test",
        },
        format="json",
    )

    assert response.status_code == 201
    assert DiagnosticTest.objects.count() == 1


@pytest.mark.django_db
def test_admin_can_create_centre_test(admin_user):
    centre = DiagnosticCentre.objects.create(
        name="Apollo",
        location="Delhi",
    )

    test = DiagnosticTest.objects.create(
        name="Blood Test",
    )

    client = APIClient()
    client.force_authenticate(user=admin_user)

    response = client.post(
        "/api/v1/catalogue/centre-tests/",
        {
            "centre": centre.id,
            "test": test.id,
            "price": "500.00",
            "is_available": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert CentreTest.objects.count() == 1

@pytest.mark.django_db
def test_centres_are_paginated(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)

    for i in range(15):
        response = client.post(
            "/api/v1/catalogue/centres/",
            {
                "name": f"Centre {i}",
                "location": f"Location {i}",
            },
            format="json",
        )
        assert response.status_code == 201

    response = client.get(
        "/api/v1/catalogue/centres/"
    )

    assert response.status_code == 200
    assert response.data["count"] == 15
    assert len(response.data["results"]) == 10
    assert response.data["next"] is not None
    assert response.data["previous"] is None

@pytest.mark.django_db
def test_centres_second_page(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)

    for i in range(15):
        DiagnosticCentre.objects.create(
            name=f"Centre {i}",
            location=f"Location {i}",
        )

    response = client.get(
        "/api/v1/catalogue/centres/?page=2"
    )

    assert response.status_code == 200
    assert response.data["count"] == 15
    assert len(response.data["results"]) == 5
    assert response.data["previous"] is not None