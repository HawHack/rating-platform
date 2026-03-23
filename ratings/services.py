from django.db.models import Sum
from users.models import User
from events.models import EventParticipation


LEVELS = [
    ('Новичок', 0),
    ('Активист', 100),
    ('Кадровый резерв', 250),
    ('Лидер', 500),
]


def get_user_rating(user):
    if not user.is_authenticated:
        return 0

    result = EventParticipation.objects.filter(
        participant=user,
        status='confirmed'
    ).aggregate(total_points=Sum('earned_points'))

    return result['total_points'] or 0


def get_user_confirmed_events_count(user):
    if not user.is_authenticated:
        return 0

    return EventParticipation.objects.filter(
        participant=user,
        status='confirmed'
    ).count()


def get_leaderboard(direction=None, city=None):
    queryset = User.objects.filter(role='participant')

    if direction:
        queryset = queryset.filter(direction=direction)

    if city:
        queryset = queryset.filter(city__icontains=city)

    leaderboard = []
    for user in queryset:
        participations = EventParticipation.objects.filter(
            participant=user,
            status='confirmed'
        )
        total_rating = participations.aggregate(total=Sum('earned_points'))['total'] or 0
        confirmed_count = participations.count()

        leaderboard.append({
            'user': user,
            'rating': total_rating,
            'confirmed_events_count': confirmed_count,
        })

    leaderboard.sort(key=lambda x: x['rating'], reverse=True)
    return leaderboard[:100]


def get_user_rank(user):
    leaderboard = get_leaderboard()
    for index, item in enumerate(leaderboard, start=1):
        if item['user'].id == user.id:
            return index
    return None


def get_user_portfolio(user):
    return EventParticipation.objects.filter(
        participant=user,
        status='confirmed'
    ).select_related('event', 'event__organizer').order_by('-confirmed_at', '-created_at')


def get_level_info(points):
    current_level = LEVELS[0][0]
    next_level = None
    points_to_next = 0

    for i, (level_name, min_points) in enumerate(LEVELS):
        if points >= min_points:
            current_level = level_name
            if i + 1 < len(LEVELS):
                next_level_name, next_level_points = LEVELS[i + 1]
                next_level = next_level_name
                points_to_next = max(0, next_level_points - points)
            else:
                next_level = None
                points_to_next = 0

    return {
        'current_level': current_level,
        'next_level': next_level,
        'points_to_next': points_to_next,
    }