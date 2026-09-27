import pytest
from rest_framework.test import APIClient
from accounts.models import User


@pytest.mark.django_db
def test_user_signup():
    client = APIClient()

    response = client.post(
        "/api/v1/accounts/signup/",
        {
            "email": "user@example.com",
            "name": "Test User",
            "password": "password123",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["email"] == "user@example.com"
    assert User.objects.filter(
        email="user@example.com"
    ).exists()


@pytest.mark.django_db
def test_duplicate_email_rejected():
    User.objects.create_user(
        email="user@example.com",
        name="Existing User",
        password="password123",
    )

    client = APIClient()

    response = client.post(
        "/api/v1/accounts/signup/",
        {
            "email": "user@example.com",
            "name": "Another User",
            "password": "password123",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_returns_jwt():
    User.objects.create_user(
        email="user@example.com",
        name="Test User",
        password="password123",
    )

    client = APIClient()

    response = client.post(
        "/api/v1/auth/token/",
        {
            "email": "user@example.com",
            "password": "password123",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_current_user():
    user = User.objects.create_user(
        email="user@example.com",
        name="Test User",
        password="password123",
    )

    client = APIClient()

    response = client.post(
        "/api/v1/auth/token/",
        {
            "email": "user@example.com",
            "password": "password123",
        },
    )

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
    )

    response = client.get("/api/v1/accounts/me/")

    assert response.status_code == 200
    assert response.data["email"] == user.email