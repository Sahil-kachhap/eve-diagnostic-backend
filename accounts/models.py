from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from accounts.managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        USER = "USER", "User"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.email
