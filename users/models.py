from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('participant', 'Участник'),
        ('organizer', 'Организатор'),
        ('observer', 'Наблюдатель'),
    ]

    DIRECTION_CHOICES = [
        ('IT', 'IT'),
        ('Media', 'Медиа'),
        ('Social', 'Социальное проектирование'),
    ]

    full_name = models.CharField(max_length=255, verbose_name='ФИО', blank=True)
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant', verbose_name='Роль')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name='Возраст')
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, blank=True, verbose_name='Направление')
    is_approved_organizer = models.BooleanField(default=False, verbose_name='Организатор одобрен')

    def __str__(self):
        return self.username