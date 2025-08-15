# channels/admin.py

from django.contrib import admin
from .models import Channel, SubscriptionTask, UserSubscription


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('title', 'username', 'owner', 'category', 'balance', 'is_active', 'is_verified')
    list_filter = ('category', 'is_active', 'is_verified')
    search_fields = ('title', 'username', 'channel_id')


@admin.register(SubscriptionTask)
class SubscriptionTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'channel', 'is_completed', 'points_earned', 'created_at')
    list_filter = ('is_completed',)
    search_fields = ('user__username', 'channel__title')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'channel', 'subscribed_at')
    search_fields = ('user__username', 'channel__title')
