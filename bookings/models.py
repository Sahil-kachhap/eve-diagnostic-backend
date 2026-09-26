from django.conf import settings
from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bookings",
    )

    centre_test = models.ForeignKey(
        "catalogue.CentreTest",
        on_delete=models.PROTECT,
        related_name="bookings",
    )

    appointment_at = models.DateTimeField()

    # Snapshot of price at booking time
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="booking_amount_positive",
            ),
        ]

    def __str__(self):
        return f"Booking {self.id}"