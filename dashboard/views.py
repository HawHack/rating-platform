import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from users.models import User
from events.models import Event, EventParticipation


def home_view(request):
    latest_events = Event.objects.select_related('organizer').order_by('-created_at')[:6]

    popular_directions_qs = (
        Event.objects.values('direction')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    popular_directions = []
    for item in popular_directions_qs:
        popular_directions.append({
            'direction': item['direction'],
            'total': item['total'],
        })

    chart_labels = []
    chart_data = []

    if request.user.is_authenticated:
        participations = (
            EventParticipation.objects.filter(
                participant=request.user,
                status='confirmed'
            )
            .select_related('event')
            .order_by('confirmed_at', 'created_at')
        )

        total_points = 0
        for participation in participations:
            total_points += participation.earned_points
            date_label = (
                participation.confirmed_at.strftime('%d.%m.%Y')
                if participation.confirmed_at
                else participation.created_at.strftime('%d.%m.%Y')
            )
            chart_labels.append(date_label)
            chart_data.append(total_points)

    context = {
        'latest_events': latest_events,
        'popular_directions': popular_directions,
        'chart_labels_json': json.dumps(chart_labels, ensure_ascii=False),
        'chart_data_json': json.dumps(chart_data),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def inspector_dashboard_view(request):
    if request.user.role != 'observer':
        messages.error(request, 'Доступ разрешен только кадровой службе.')
        return redirect('home')

    participants = User.objects.filter(role='participant')

    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    city = request.GET.get('city')
    direction = request.GET.get('direction')
    min_rating = request.GET.get('min_rating')
    min_events = request.GET.get('min_events')

    if age_min:
        participants = participants.filter(age__gte=age_min)

    if age_max:
        participants = participants.filter(age__lte=age_max)

    if city:
        participants = participants.filter(city__icontains=city)

    if direction:
        participants = participants.filter(direction=direction)

    candidate_rows = []

    for participant in participants:
        confirmed_participations = EventParticipation.objects.filter(
            participant=participant,
            status='confirmed'
        )

        total_rating = confirmed_participations.aggregate(
            total=Sum('earned_points')
        )['total'] or 0

        events_count = confirmed_participations.count()

        avg_score = confirmed_participations.aggregate(
            avg=Avg('earned_points')
        )['avg'] or 0

        candidate_rows.append({
            'user': participant,
            'rating': total_rating,
            'events_count': events_count,
            'avg_score': round(avg_score, 1) if avg_score else 0,
        })

    if min_rating:
        candidate_rows = [row for row in candidate_rows if row['rating'] >= int(min_rating)]

    if min_events:
        candidate_rows = [row for row in candidate_rows if row['events_count'] >= int(min_events)]

    candidate_rows.sort(key=lambda x: x['rating'], reverse=True)

    context = {
        'candidate_rows': candidate_rows,
        'direction_choices': User.DIRECTION_CHOICES,
        'filters': {
            'age_min': age_min or '',
            'age_max': age_max or '',
            'city': city or '',
            'direction': direction or '',
            'min_rating': min_rating or '',
            'min_events': min_events or '',
        }
    }
    return render(request, 'dashboard/inspector_dashboard.html', context)


@login_required
def candidate_report_view(request, user_id):
    if request.user.role != 'observer':
        messages.error(request, 'Доступ разрешен только кадровой службе.')
        return redirect('home')

    candidate = get_object_or_404(User, id=user_id, role='participant')

    confirmed_participations = EventParticipation.objects.filter(
        participant=candidate,
        status='confirmed'
    ).select_related('event', 'event__organizer').order_by('-confirmed_at', '-created_at')

    total_rating = confirmed_participations.aggregate(total=Sum('earned_points'))['total'] or 0
    events_count = confirmed_participations.count()
    avg_score = confirmed_participations.aggregate(avg=Avg('earned_points'))['avg'] or 0

    context = {
        'candidate': candidate,
        'confirmed_participations': confirmed_participations,
        'total_rating': total_rating,
        'events_count': events_count,
        'avg_score': round(avg_score, 1) if avg_score else 0,
    }
    return render(request, 'dashboard/candidate_report.html', context)