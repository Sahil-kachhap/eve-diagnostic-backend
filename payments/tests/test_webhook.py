import hashlib
import hmac
import json
from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from bookings.models import Booking
from catalogue.models import (
    CentreTest,
    DiagnosticCentre,
    DiagnosticTest,
)
from payments.models import Payment, PaymentEvent


def sign_payload(payload):
    return hmac.new(
        settings.PAYMENT_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

@pytest.fixture
def payment():
    user = User.objects.create_user(
        email="user@example.com",
        name="Test User",
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
        user=user,
        centre_test=centre_test,
        appointment_at=timezone.now() + timedelta(days=1),
        amount="500.00",
        status=Booking.Status.PENDING,
    )

    return Payment.objects.create(
        booking=booking,
        provider_payment_id="mock_test123",
        amount="500.00",
        status=Payment.Status.PENDING,
    )


@pytest.mark.django_db
def test_successful_webhook(payment):
    payload = {
        "event_id": "evt_001",
        "event_type": "payment.success",
        "provider_payment_id": payment.provider_payment_id,
        "status": "SUCCESS",
        "amount": "500.00",
    }

    raw_payload = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    signature = sign_payload(raw_payload)

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_WEBHOOK_SIGNATURE=signature,
    )

    assert response.status_code == 200

    payment.refresh_from_db()
    payment.booking.refresh_from_db()

    assert payment.status == Payment.Status.SUCCESS
    assert (
        payment.booking.status
        == Booking.Status.CONFIRMED
    )

    assert PaymentEvent.objects.filter(
        event_id="evt_001"
    ).exists()


@pytest.mark.django_db
def test_failed_webhook(payment):
    payload = {
        "event_id": "evt_002",
        "event_type": "payment.failed",
        "provider_payment_id": payment.provider_payment_id,
        "status": "FAILED",
        "amount": "500.00",
    }

    raw_payload = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    signature = sign_payload(raw_payload)

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_WEBHOOK_SIGNATURE=signature,
    )

    assert response.status_code == 200

    payment.refresh_from_db()
    payment.booking.refresh_from_db()

    assert payment.status == Payment.Status.FAILED
    assert payment.booking.status == Booking.Status.FAILED

@pytest.mark.django_db
def test_duplicate_webhook_is_idempotent(payment):
    payload = {
        "event_id": "evt_duplicate",
        "event_type": "payment.success",
        "provider_payment_id": payment.provider_payment_id,
        "status": "SUCCESS",
        "amount": "500.00",
    }

    raw_payload = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    signature = sign_payload(raw_payload)

    client = APIClient()

    first_response = client.post(
        "/api/v1/payments/webhook/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_WEBHOOK_SIGNATURE=signature,
    )

    second_response = client.post(
        "/api/v1/payments/webhook/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_WEBHOOK_SIGNATURE=signature,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert PaymentEvent.objects.filter(
        event_id="evt_duplicate"
    ).count() == 1

    assert Payment.objects.filter(
        provider_payment_id=payment.provider_payment_id
    ).count() == 1

    payment.refresh_from_db()

    assert payment.status == Payment.Status.SUCCESS

@pytest.mark.django_db
def test_invalid_webhook_signature(payment):
    payload = {
        "event_id": "evt_invalid",
        "event_type": "payment.success",
        "provider_payment_id": payment.provider_payment_id,
        "status": "SUCCESS",
        "amount": "500.00",
    }

    raw_payload = json.dumps(payload).encode()

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_WEBHOOK_SIGNATURE="invalid-signature",
    )

    assert response.status_code == 401

    payment.refresh_from_db()

    assert payment.status == Payment.Status.PENDING
    assert PaymentEvent.objects.count() == 0

@pytest.mark.django_db
def test_webhook_rejects_amount_mismatch(payment):
    payload = {
        "event_id": "evt_wrong_amount",
        "event_type": "payment.success",
        "provider_payment_id": payment.provider_payment_id,
        "status": "SUCCESS",
        "amount": "999.00",
    }

    raw_payload = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    signature = sign_payload(raw_payload)

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_WEBHOOK_SIGNATURE=signature,
    )

    assert response.status_code == 400

    payment.refresh_from_db()

    assert payment.status == Payment.Status.PENDING


@pytest.mark.django_db
def test_payment_cannot_transition_from_success_to_failed(
    payment,
):
    from payments.services import transition_payment
    from rest_framework.exceptions import ValidationError

    payment.status = Payment.Status.SUCCESS
    payment.save()

    with pytest.raises(ValidationError):
        transition_payment(
            payment=payment,
            new_status=Payment.Status.FAILED,
        )

@pytest.mark.django_db
def test_confirmed_booking_cannot_be_cancelled(payment):
    from bookings.services import cancel_booking
    from rest_framework.exceptions import ValidationError

    booking = payment.booking

    booking.status = Booking.Status.CONFIRMED
    booking.save()

    with pytest.raises(ValidationError):
        cancel_booking(
            user=booking.user,
            booking_id=booking.id,
        )

