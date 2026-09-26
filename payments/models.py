from django.db import models

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    provider_payment_id = models.CharField(
        max_length=100,
        unique=True,
    )

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
                name="payment_amount_positive",
            ),
        ]

    def __str__(self):
        return self.provider_payment_id

class PaymentEvent(models.Model):
    event_id = models.CharField(
        max_length=150,
        unique=True,
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="events",
    )

    event_type = models.CharField(
        max_length=100,
    )

    payload = models.JSONField()

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id

