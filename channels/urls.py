# channels/urls.py

from django.urls import path
from .views import (
    ChannelListView, add_channel,
    get_subscription_task, confirm_subscription,
     distribute_points,user_channels
)

urlpatterns = [
    path('channels/', ChannelListView.as_view(), name='channel-list'),
    path('add-channel/', add_channel, name='add-channel'),
    path('get-task/', get_subscription_task, name='get-task'),
    path('confirm-subscription/', confirm_subscription, name='confirm-subscription'),
    path('user-channels/<int:user_id>/', user_channels, name='user-channels'),  # Новый endpoint
    path('distribute-points/', distribute_points, name='distribute-points'),
]