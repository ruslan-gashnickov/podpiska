# channels/serializers.py

from rest_framework import serializers
from .models import Channel, SubscriptionTask, UserSubscription
from users.models import User


class ChannelSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Channel
        fields = (
            'id', 'channel_id', 'title', 'username', 'category',
            'balance', 'is_active', 'is_verified', 'created_at', 'owner_username'
        )
        read_only_fields = ('balance', 'is_verified', 'created_at')


class ChannelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('channel_id', 'title', 'username', 'category')


class SubscriptionTaskSerializer(serializers.ModelSerializer):
    channel_title = serializers.CharField(source='channel.title', read_only=True)
    channel_username = serializers.CharField(source='channel.username', read_only=True)
    channel = serializers.CharField(source='channel.channel_id', read_only=True)

    class Meta:
        model = SubscriptionTask
        fields = ('id', 'channel', 'channel_title', 'channel_username', 'is_completed', 'points_earned')


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ('user', 'channel', 'subscribed_at')