import uuid

from django.conf import settings
from django.db import models


class Event(models.Model):
    DIRECTION_CHOICES = [
        ('IT', 'IT'),
        ('Media', 'Медиа'),
        ('Social', 'Социальное проектирование'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    date = models.DateTimeField(verbose_name='Дата и время')
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='Организатор'
    )
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, verbose_name='Направление')
    base_points = models.PositiveIntegerField(default=10, verbose_name='Базовые баллы')
    difficulty_coef = models.FloatField(default=1.0, verbose_name='Коэффициент сложности')
    bonus_text = models.CharField(max_length=255, blank=True, verbose_name='Бонусы')
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name='Макс. участников')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def calculated_points(self):
        return int(self.base_points * self.difficulty_coef)


class EventParticipation(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Зарегистрирован'),
        ('attended', 'Присутствовал'),
        ('confirmed', 'Подтвержден'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participations',
        verbose_name='Мероприятие'
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_participations',
        verbose_name='Участник'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', verbose_name='Статус')
    earned_points = models.PositiveIntegerField(default=0, verbose_name='Начисленные баллы')
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_participations',
        verbose_name='Кем подтверждено'
    )
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата подтверждения')
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'participant')
        verbose_name = 'Участие в мероприятии'
        verbose_name_plural = 'Участия в мероприятиях'

    def __str__(self):
        return f'{self.participant.username} - {self.event.title}'


class OrganizerReview(models.Model):
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        verbose_name='Организатор'
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_reviews',
        verbose_name='Участник'
    )
    rating = models.PositiveIntegerField(verbose_name='Оценка')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organizer', 'participant')
        verbose_name = 'Отзыв организатору'
        verbose_name_plural = 'Отзывы организаторам'

    def __str__(self):
        return f'Отзыв {self.participant.username} -> {self.organizer.username}'