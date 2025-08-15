# users/urls.py

from django.urls import path
from .views import register_user

urlpatterns = [
    path('register-user/', register_user, name='register-user'),
]