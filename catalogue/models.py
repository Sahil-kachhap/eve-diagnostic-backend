from django.db import models

class DiagnosticCenter(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class DiagnosticTest(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CentreTest(models.Model):
    centre = models.ForeignKey(
        DiagnosticCenter,
        on_delete=models.CASCADE,
        related_name="centre_tests",
    )

    test = models.ForeignKey(
        DiagnosticTest,
        on_delete=models.CASCADE,
        related_name="centre_tests",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["centre", "test"],
                name="unique_centre_test",
            ),
            models.CheckConstraint(
                condition = models.Q(price__gt=0),
                name = "centre_test_price_positive",
            ),
        ]

    def __str__(self):
        return f"{self.centre.name} - {self.test.name}"