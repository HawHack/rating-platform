from django.shortcuts import render
from .services import get_leaderboard
from users.models import User


def leaderboard_view(request):
    direction = request.GET.get('direction')
    city = request.GET.get('city')

    leaderboard = get_leaderboard(direction=direction, city=city)

    context = {
        'leaderboard': leaderboard,
        'selected_direction': direction,
        'selected_city': city,
        'direction_choices': User.DIRECTION_CHOICES,
    }
    return render(request, 'ratings/leaderboard.html', context)