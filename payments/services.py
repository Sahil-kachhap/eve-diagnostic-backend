from django.db import transaction
from rest_framework.exceptions import ValidationError

from bookings.models import Booking

from .models import Payment
from .provider import MockPaymentProvider


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