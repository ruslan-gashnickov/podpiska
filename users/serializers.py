# users/serializers.py

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'telegram_id', 'username', 'balance', 'created_at')
        read_only_fields = ('id', 'balance', 'created_at')