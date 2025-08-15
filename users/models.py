
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True)
    balance = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.telegram_id})"