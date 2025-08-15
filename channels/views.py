# channels/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import Channel, SubscriptionTask, UserSubscription
from .serializers import (
    ChannelSerializer, ChannelCreateSerializer,
    SubscriptionTaskSerializer
)
from users.models import User
from users.serializers import UserSerializer
from django.utils import timezone
from django.db import transaction


# Получение списка активных каналов
class ChannelListView(generics.ListAPIView):
    queryset = Channel.objects.filter(is_active=True, balance__gt=0)
    serializer_class = ChannelSerializer


# Добавление канала пользователем
@api_view(['POST'])
@permission_classes([AllowAny])
def add_channel(request):
    serializer = ChannelCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Проверяем, существует ли пользователь
            owner_id = request.data.get('owner_id')
            owner = User.objects.get(telegram_id=owner_id)

            # Создаем канал
            channel = serializer.save(owner=owner)

            # Возвращаем сериализованные данные
            response_serializer = ChannelSerializer(channel)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Получение задания для подписки
@api_view(['POST'])
@permission_classes([AllowAny])
def get_subscription_task(request):
    user_id = request.data.get('user_id')
    try:
        user = User.objects.get(telegram_id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Найти каналы, на которые пользователь еще не подписан и у которых есть баланс
    subscribed_channel_ids = UserSubscription.objects.filter(user=user).values_list('channel_id', flat=True)

    # Проверяем, есть ли уже активное задание
    task = SubscriptionTask.objects.filter(
        user=user,
        is_completed=False
    ).first()

    if task:
        serializer = SubscriptionTaskSerializer(task)
        return Response(serializer.data)

    # Ищем новый канал для задания
    channel = Channel.objects.filter(
        is_active=True,
        balance__gt=0
    ).exclude(
        id__in=subscribed_channel_ids
    ).exclude(
        owner=user
    ).first()

    if not channel:
        return Response({'message': 'No channels available'}, status=status.HTTP_404_NOT_FOUND)

    task, created = SubscriptionTask.objects.get_or_create(
        user=user,
        channel=channel
    )

    serializer = SubscriptionTaskSerializer(task)
    return Response(serializer.data)


# Подтверждение подписки
@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_subscription(request):
    user_id = request.data.get('user_id')
    task_id = request.data.get('task_id')

    print(f"Попытка подтверждения подписки: user_id={user_id}, task_id={task_id}")  # Отладка

    try:
        user = User.objects.get(telegram_id=user_id)
        print(f"Найден пользователь: {user.username}")  # Отладка

        task = SubscriptionTask.objects.get(id=task_id, user=user)
        print(f"Найдена задача: id={task.id}, completed={task.is_completed}")  # Отладка

        if task.is_completed:
            print("Задача уже завершена")  # Отладка
            return Response({'error': 'Task already completed'}, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        print(f"Пользователь не найден: {user_id}")  # Отладка
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except SubscriptionTask.DoesNotExist:
        print(f"Задача не найдена: user_id={user_id}, task_id={task_id}")  # Отладка
        # Проверим, существует ли задача вообще
        try:
            task_check = SubscriptionTask.objects.get(id=task_id)
            print(f"Задача существует, но принадлежит другому пользователю: {task_check.user.telegram_id}")  # Отладка
            return Response({'error': 'Task belongs to another user'}, status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionTask.DoesNotExist:
            print(f"Задача не существует: {task_id}")  # Отладка
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Ошибка при поиске задачи: {e}")  # Отладка
        return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    # Используем транзакцию для обеспечения целостности данных
    try:
        with transaction.atomic():
            # Подтверждаем подписку
            task.is_completed = True
            task.points_earned = 1
            task.completed_at = timezone.now()
            task.save()
            print(f"Задача помечена как завершенная")  # Отладка

            # Начисляем баллы пользователю
            old_balance = user.balance
            user.balance += 1
            user.save()
            print(f"Баланс пользователя обновлен: {old_balance} -> {user.balance}")  # Отладка

            # Списываем баллы у канала (если есть баллы)
            channel = task.channel
            old_channel_balance = channel.balance
            if channel.balance > 0:
                channel.balance -= 1
                channel.save()
                print(f"Баланс канала обновлен: {old_channel_balance} -> {channel.balance}")  # Отладка
            else:
                print(f"У канала недостаточно баллов: {channel.balance}")  # Отладка

            # Добавляем в подписки пользователя (если еще не подписан)
            subscription, created = UserSubscription.objects.get_or_create(
                user=user,
                channel=channel
            )
            print(f"Подписка создана: {created}")  # Отладка

            response_data = {
                'message': 'Subscription confirmed',
                'points': 1,
                'new_balance': user.balance,
                'subscription_created': created
            }
            print(f"Отправляем ответ: {response_data}")  # Отладка

            return Response(response_data)

    except Exception as e:
        print(f"Ошибка при подтверждении подписки: {e}")  # Отладка
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Отладка
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Получение каналов пользователя
@api_view(['GET'])
@permission_classes([AllowAny])
def user_channels(request, user_id):
    try:
        user = User.objects.get(telegram_id=user_id)
        channels = Channel.objects.filter(owner=user)
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Распределение баллов
@api_view(['POST'])
@permission_classes([AllowAny])
def distribute_points(request):
    user_id = request.data.get('user_id')
    channel_id = request.data.get('channel_id')
    points = request.data.get('points')

    try:
        user = User.objects.get(telegram_id=user_id)
        channel = Channel.objects.get(id=channel_id, owner=user)

        if points > user.balance:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        # Переводим баллы
        user.balance -= points
        channel.balance += points

        user.save()
        channel.save()

        return Response({
            'message': 'Points distributed successfully',
            'user_balance': user.balance,
            'channel_balance': channel.balance
        })

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Channel.DoesNotExist:
        return Response({'error': 'Channel not found or not owned by user'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)