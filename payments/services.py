from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from bookings.models import Booking
from bookings.services import transition_booking

from .models import Payment, PaymentEvent
from .provider import MockPaymentProvider

import hashlib
import hmac

from django.conf import settings


@transaction.atomic
def create_payment(*, user, booking_id):
    try:
        booking = (
            Booking.objects
            .select_for_update()
            .get(
                id=booking_id,
                user=user,
            )
        )
    except Booking.DoesNotExist:
        raise ValidationError({
            "booking": "Booking not found."
        })

    if booking.status != Booking.Status.PENDING:
        raise ValidationError({
            "booking": (
                f"Payment cannot be created for a booking "
                f"in {booking.status} state."
            )
        })

    existing_payment = (
        Payment.objects
        .filter(
            booking=booking,
            status__in=[
                Payment.Status.PENDING,
                Payment.Status.SUCCESS,
            ],
        )
        .first()
    )

    if existing_payment:
        return existing_payment

    provider_response = MockPaymentProvider.create_payment(
        amount=booking.amount,
    )

    payment = Payment.objects.create(
        booking=booking,
        provider_payment_id=provider_response[
            "provider_payment_id"
        ],
        amount=booking.amount,
        status=Payment.Status.PENDING,
    )

    return payment

def transition_payment(*, payment, new_status):
    allowed_transitions = {
        Payment.Status.PENDING: {
            Payment.Status.SUCCESS,
            Payment.Status.FAILED,
        },
        Payment.Status.SUCCESS: set(),
        Payment.Status.FAILED: set(),
    }

    allowed = allowed_transitions.get(
        payment.status,
        set(),
    )

    if new_status not in allowed:
        raise ValidationError({
            "status": (
                f"Cannot transition payment from "
                f"{payment.status} to {new_status}."
            )
        })

    payment.status = new_status
    payment.save(
        update_fields=["status", "updated_at"]
    )

    return payment


def validate_webhook_signature(*, payload, signature):
    expected_signature = hmac.new(
        settings.PAYMENT_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


@transaction.atomic
def process_payment_webhook(
    *,
    event_id,
    event_type,
    provider_payment_id,
    status,
    amount,
    payload,
):
    # 1. Idempotency check
    existing_event = (
        PaymentEvent.objects
        .filter(event_id=event_id)
        .first()
    )

    if existing_event:
        return existing_event.payment

    # 2. Lock the payment row
    try:
        payment = (
            Payment.objects
            .select_for_update()
            .select_related("booking")
            .get(
                provider_payment_id=provider_payment_id
            )
        )
    except Payment.DoesNotExist:
        raise ValidationError({
            "provider_payment_id": "Payment not found."
        })

    # 3. Verify webhook amount
    if amount != payment.amount:
        raise ValidationError({
            "amount": "Payment amount does not match."
        })

    # 4. Make sure payment is still processable
    if payment.status != Payment.Status.PENDING:
        raise ValidationError({
            "status": (
                f"Payment is already in "
                f"{payment.status} state."
            )
        })

    # 5. Determine new payment status
    if status == "SUCCESS":
        new_payment_status = Payment.Status.SUCCESS
    else:
        new_payment_status = Payment.Status.FAILED

    # 6. Update payment
    payment.status = new_payment_status
    payment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    # 7. Store webhook event
    PaymentEvent.objects.create(
        event_id=event_id,
        payment=payment,
        event_type=event_type,
        payload=payload,
        processed_at=timezone.now(),
    )

    # 8. Update booking
    if new_payment_status == Payment.Status.SUCCESS:
        transition_booking(
            booking=payment.booking,
            new_status=payment.booking.Status.CONFIRMED,
        )
    else:
        transition_booking(
            booking=payment.booking,
            new_status=payment.booking.Status.FAILED,
        )

    return payment