# users/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    telegram_id = request.data.get('telegram_id')
    username = request.data.get('username')

    try:
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': username}
        )

        serializer = UserSerializer(user)
        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)