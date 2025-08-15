# channels/models.py

from django.db import models
from users.models import User


class Channel(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Технологии'),
        ('edu', 'Образование'),
        ('ent', 'Развлечения'),
        ('news', 'Новости'),
        ('other', 'Другое'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_channels')
    channel_id = models.BigIntegerField(help_text="ID канала в Telegram")
    title = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, null=True, help_text="Username канала (@username)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    balance = models.IntegerField(default=5, help_text="Баланс для заданий")
    is_active = models.BooleanField(default=True, help_text="Активен ли канал в системе")
    is_verified = models.BooleanField(default=False, help_text="Проверен ли канал администратором")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'channel_id')

    def __str__(self):
        return f"{self.title} (@{self.username})"


class SubscriptionTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription_tasks')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subscription_tasks')
    is_completed = models.BooleanField(default=False)
    points_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'channel')

    def __str__(self):
        return f"{self.user.username} -> {self.channel.title}"


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'channel')  # Это правильно

    def __str__(self):
        return f"{self.user.username} subscribed to {self.channel.title}"