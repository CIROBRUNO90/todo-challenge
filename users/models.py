from django.contrib.auth.models import AbstractUser
from django.db import models


class Users(AbstractUser):

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        null=False,
        blank=False,
    )
    phone_number = models.CharField(max_length=255, null=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email

    class Meta:
        """
        Meta method for the User model.
        """
        db_table = "users"
