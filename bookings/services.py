from django.db import transaction
from rest_framework.exceptions import ValidationError

from catalogue.models import CentreTest
from .models import Booking


@transaction.atomic
def create_booking(*, user, centre_test_id, appointment_at):
    try:
        centre_test = (
            CentreTest.objects
            .select_for_update()
            .select_related("centre", "test")
            .get(id=centre_test_id)
        )
    except CentreTest.DoesNotExist:
        raise ValidationError({
            "centre_test": "Centre test does not exist."
        })

    if not centre_test.is_available:
        raise ValidationError({
            "centre_test": "This test is currently unavailable."
        })

    if appointment_at is None:
        raise ValidationError({
            "appointment_at": "Appointment time is required."
        })

    booking = Booking.objects.create(
        user=user,
        centre_test=centre_test,
        appointment_at=appointment_at,
        amount=centre_test.price,
        status=Booking.Status.PENDING,
    )

    return booking

@transaction.atomic
def cancel_booking(*, user, booking_id):
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
            "detail": "Booking not found."
        })

    

    return transition_booking(booking=booking, new_status=Booking.Status.CANCELLED)

def transition_booking(
    *,
    booking,
    new_status,
):
    allowed_transitions = {
        Booking.Status.PENDING: {
            Booking.Status.CONFIRMED,
            Booking.Status.FAILED,
            Booking.Status.CANCELLED,
        },
        Booking.Status.CONFIRMED: set(),
        Booking.Status.FAILED: set(),
        Booking.Status.CANCELLED: set(),
    }

    allowed = allowed_transitions.get(
        booking.status,
        set(),
    )

    if new_status not in allowed:
        raise ValidationError({
            "status": (
                f"Cannot transition booking from "
                f"{booking.status} to {new_status}."
            )
        })

    booking.status = new_status
    booking.save(
        update_fields=["status", "updated_at"]
    )

    return booking