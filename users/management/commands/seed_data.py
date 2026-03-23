import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from events.models import Event, EventParticipation, OrganizerReview


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Очистка старых тестовых данных...'))

        OrganizerReview.objects.all().delete()
        EventParticipation.objects.all().delete()
        Event.objects.all().delete()

        # Удаляем только не-superuser пользователей, чтобы админ остался
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('Старые данные удалены.'))

        cities = ['Алматы', 'Астана', 'Шымкент', 'Караганда', 'Тараз', 'Актобе']
        directions = ['IT', 'Media', 'Social']
        bonus_options = [
            'Мерч',
            'Билеты',
            'Приглашение на форум',
            'Встреча с экспертом',
            'Стажировка',
            'Сертификат',
        ]

        participant_names = [
            'Айдар Смагулов', 'Алина Касымова', 'Диас Абдрахманов', 'Ерке Нурланова',
            'Жанна Сарсенова', 'Ильяс Мухамедов', 'Камила Ержанова', 'Марат Тлеубаев',
            'Назерке Ашимова', 'Олжас Ибраев', 'Раушан Бекова', 'Санжар Турсынов',
            'Тимур Жаксылыков', 'Ульяна Серикова', 'Фариза Есенова', 'Шерхан Кайратов',
            'Эльмира Бахытжан', 'Юлия Соколова', 'Ясмин Ахметова', 'Руслан Каримов',
        ]

        organizer_names = [
            'Иван Иванов', 'Мария Петрова', 'Нурбек Сеитов'
        ]

        observer_names = [
            'Кадровик Смирнов', 'HR Ахметова'
        ]

        self.stdout.write(self.style.WARNING('Создание организаторов...'))
        organizers = []
        for i, name in enumerate(organizer_names, start=1):
            username = f'organizer{i}'
            user = User.objects.create_user(
                username=username,
                password='12345678Qq',
                email=f'{username}@mail.com',
                full_name=name,
                role='organizer',
                city=random.choice(cities),
                age=random.randint(22, 35),
                direction=random.choice(directions),
                is_approved_organizer=True,
            )
            organizers.append(user)

        self.stdout.write(self.style.SUCCESS(f'Создано организаторов: {len(organizers)}'))

        self.stdout.write(self.style.WARNING('Создание участников...'))
        participants = []
        for i, name in enumerate(participant_names, start=1):
            username = f'participant{i}'
            user = User.objects.create_user(
                username=username,
                password='12345678Qq',
                email=f'{username}@mail.com',
                full_name=name,
                role='participant',
                city=random.choice(cities),
                age=random.randint(16, 28),
                direction=random.choice(directions),
            )
            participants.append(user)

        self.stdout.write(self.style.SUCCESS(f'Создано участников: {len(participants)}'))

        self.stdout.write(self.style.WARNING('Создание наблюдателей...'))
        observers = []
        for i, name in enumerate(observer_names, start=1):
            username = f'observer{i}'
            user = User.objects.create_user(
                username=username,
                password='12345678Qq',
                email=f'{username}@mail.com',
                full_name=name,
                role='observer',
                city=random.choice(cities),
                age=random.randint(25, 40),
                direction=random.choice(directions),
            )
            observers.append(user)

        self.stdout.write(self.style.SUCCESS(f'Создано наблюдателей: {len(observers)}'))

        self.stdout.write(self.style.WARNING('Создание мероприятий...'))
        event_titles = [
            'IT-Форум молодежи',
            'Школа медиа-лидеров',
            'Социальный проектный интенсив',
            'Хакатон цифровых решений',
            'Молодежный форум инициатив',
            'Мастер-класс по публичным выступлениям',
            'Семинар по социальному дизайну',
            'Конкурс медиапроектов',
            'Круглый стол по инновациям',
            'Дебаты молодежного парламента',
            'Лекция по лидерству',
            'Воркшоп по созданию стартапов',
            'Практикум по SMM',
            'Форум волонтерских проектов',
            'Проектная сессия по городским инициативам',
        ]

        events = []
        for i, title in enumerate(event_titles):
            organizer = random.choice(organizers)
            base_points = random.choice([10, 15, 20, 25, 30])
            difficulty_coef = random.choice([1.0, 1.2, 1.5, 2.0])

            event = Event.objects.create(
                title=title,
                description=f'Описание мероприятия: {title}. Это тестовое мероприятие для демонстрации платформы.',
                date=timezone.now() - timedelta(days=random.randint(1, 60)),
                organizer=organizer,
                direction=random.choice(directions),
                base_points=base_points,
                difficulty_coef=difficulty_coef,
                bonus_text=random.choice(bonus_options),
                max_participants=random.choice([20, 30, 50, 100]),
            )
            events.append(event)

        self.stdout.write(self.style.SUCCESS(f'Создано мероприятий: {len(events)}'))

        self.stdout.write(self.style.WARNING('Создание участий...'))
        participations_created = 0

        for event in events:
            selected_participants = random.sample(participants, random.randint(5, 12))

            for participant in selected_participants:
                status = random.choices(
                    ['registered', 'confirmed'],
                    weights=[30, 70],
                    k=1
                )[0]

                earned_points = event.calculated_points() if status == 'confirmed' else 0
                confirmed_at = timezone.now() - timedelta(days=random.randint(0, 30)) if status == 'confirmed' else None
                confirmed_by = event.organizer if status == 'confirmed' else None

                EventParticipation.objects.create(
                    event=event,
                    participant=participant,
                    status=status,
                    earned_points=earned_points,
                    confirmed_at=confirmed_at,
                    confirmed_by=confirmed_by,
                )
                participations_created += 1

        self.stdout.write(self.style.SUCCESS(f'Создано участий: {participations_created}'))

        self.stdout.write(self.style.WARNING('Создание отзывов организаторам...'))
        reviews_created = 0

        for organizer in organizers:
            reviewers = random.sample(participants, random.randint(3, 6))

            for participant in reviewers:
                OrganizerReview.objects.create(
                    organizer=organizer,
                    participant=participant,
                    rating=random.randint(3, 5),
                    comment=random.choice([
                        'Отличная организация мероприятия.',
                        'Очень полезное событие и хороший спикерский состав.',
                        'Все прошло на высоком уровне.',
                        'Понравился формат и обратная связь.',
                        'Хорошая атмосфера и полезные знакомства.',
                    ])
                )
                reviews_created += 1

        self.stdout.write(self.style.SUCCESS(f'Создано отзывов: {reviews_created}'))

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены!'))
        self.stdout.write(self.style.SUCCESS('Тестовые аккаунты:'))
        self.stdout.write('Организатор: organizer1 / 12345678Qq')
        self.stdout.write('Участник: participant1 / 12345678Qq')
        self.stdout.write('Наблюдатель: observer1 / 12345678Qq')