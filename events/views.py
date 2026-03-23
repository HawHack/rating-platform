from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from users.models import User
from .forms import EventForm, OrganizerReviewForm
from .models import Event, EventParticipation, OrganizerReview


def event_list_view(request):
    events = Event.objects.select_related('organizer').order_by('date')

    direction = request.GET.get('direction')
    status = request.GET.get('status')

    if direction:
        events = events.filter(direction=direction)

    if status == 'upcoming':
        events = events.filter(date__gte=timezone.now())
    elif status == 'past':
        events = events.filter(date__lt=timezone.now())

    context = {
        'events': events,
        'selected_direction': direction,
        'selected_status': status,
        'direction_choices': Event.DIRECTION_CHOICES,
    }
    return render(request, 'events/event_list.html', context)


def event_detail_view(request, event_id):
    event = get_object_or_404(Event.objects.select_related('organizer'), id=event_id)

    participation = None
    checkin_url = None

    if request.user.is_authenticated and request.user.role == 'participant':
        participation = EventParticipation.objects.filter(
            event=event,
            participant=request.user
        ).first()

        if participation:
            checkin_url = request.build_absolute_uri(
                f'/events/checkin/{participation.qr_token}/'
            )

    context = {
        'event': event,
        'participation': participation,
        'checkin_url': checkin_url,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def event_create_view(request):
    if request.user.role != 'organizer':
        messages.error(request, 'Только организатор может создавать мероприятия.')
        return redirect('event_list')

    if not request.user.is_approved_organizer:
        messages.warning(request, 'Ваш аккаунт организатора еще не одобрен.')
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Мероприятие успешно создано.')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {'form': form, 'page_title': 'Создать мероприятие'})


@login_required
def event_update_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user != event.organizer:
        messages.error(request, 'Вы не можете редактировать это мероприятие.')
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Мероприятие обновлено.')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'page_title': 'Редактировать мероприятие'})


@login_required
def register_for_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user.role != 'participant':
        messages.error(request, 'Записываться на мероприятие могут только участники.')
        return redirect('event_detail', event_id=event.id)

    participation, created = EventParticipation.objects.get_or_create(
        event=event,
        participant=request.user,
        defaults={'status': 'registered'}
    )

    if created:
        messages.success(request, 'Вы успешно записались на мероприятие.')
    else:
        messages.info(request, 'Вы уже записаны на это мероприятие.')

    return redirect('event_detail', event_id=event.id)


@login_required
def my_events_view(request):
    participations = EventParticipation.objects.filter(
        participant=request.user
    ).select_related('event', 'event__organizer').order_by('-created_at')

    return render(request, 'events/my_events.html', {'participations': participations})


@login_required
def organizer_event_participants_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user != event.organizer:
        messages.error(request, 'Вы не можете просматривать участников этого мероприятия.')
        return redirect('event_detail', event_id=event.id)

    participations = EventParticipation.objects.filter(
        event=event
    ).select_related('participant').order_by('-created_at')

    return render(request, 'events/event_participants.html', {
        'event': event,
        'participations': participations,
    })


@login_required
def confirm_participation_view(request, participation_id):
    participation = get_object_or_404(EventParticipation, id=participation_id)
    event = participation.event

    if request.user != event.organizer:
        messages.error(request, 'Только организатор этого мероприятия может подтверждать участие.')
        return redirect('event_detail', event_id=event.id)

    if participation.status != 'confirmed':
        participation.status = 'confirmed'
        participation.earned_points = int(event.base_points * event.difficulty_coef)
        participation.confirmed_by = request.user
        participation.confirmed_at = timezone.now()
        participation.save()
        messages.success(request, 'Участие подтверждено, баллы начислены.')
    else:
        messages.info(request, 'Это участие уже подтверждено.')

    return redirect('organizer_event_participants', event_id=event.id)


@login_required
def checkin_by_qr_view(request, token):
    participation = get_object_or_404(EventParticipation, qr_token=token)

    if request.user.role != 'participant':
        messages.error(request, 'QR check-in доступен только участникам.')
        return redirect('event_detail', event_id=participation.event.id)

    if participation.participant != request.user:
        messages.error(request, 'Этот QR-код не принадлежит вашему участию.')
        return redirect('event_detail', event_id=participation.event.id)

    if participation.status == 'registered':
        participation.status = 'attended'
        participation.save()
        messages.success(request, 'Присутствие отмечено через QR. Ожидайте подтверждения организатора.')
    elif participation.status == 'attended':
        messages.info(request, 'Вы уже отметили присутствие по QR.')
    elif participation.status == 'confirmed':
        messages.info(request, 'Ваше участие уже подтверждено организатором.')

    return redirect('event_detail', event_id=participation.event.id)


def organizer_detail_view(request, organizer_id):
    organizer = get_object_or_404(User, id=organizer_id, role='organizer')

    events = Event.objects.filter(organizer=organizer).order_by('-date')
    reviews = OrganizerReview.objects.filter(organizer=organizer).select_related('participant').order_by('-created_at')
    reviews_count = reviews.count()

    trust_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    events_count = events.count()

    bonus_list = list(
        events.exclude(bonus_text='')
        .values_list('bonus_text', flat=True)
        .distinct()
    )

    existing_review = None
    can_leave_review = False

    if request.user.is_authenticated and request.user.role == 'participant':
        existing_review = OrganizerReview.objects.filter(
            organizer=organizer,
            participant=request.user
        ).first()

        if organizer != request.user and not existing_review:
            can_leave_review = True

    context = {
        'organizer': organizer,
        'events': events,
        'events_count': events_count,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'trust_rating': trust_rating,
        'bonus_list': bonus_list,
        'existing_review': existing_review,
        'can_leave_review': can_leave_review,
    }
    return render(request, 'events/organizer_detail.html', context)


@login_required
def add_organizer_review_view(request, organizer_id):
    organizer = get_object_or_404(User, id=organizer_id, role='organizer')

    if request.user.role != 'participant':
        messages.error(request, 'Отзывы могут оставлять только участники.')
        return redirect('organizer_detail', organizer_id=organizer.id)

    if organizer == request.user:
        messages.error(request, 'Нельзя оставить отзыв самому себе.')
        return redirect('organizer_detail', organizer_id=organizer.id)

    existing_review = OrganizerReview.objects.filter(
        organizer=organizer,
        participant=request.user
    ).first()

    if existing_review:
        messages.info(request, 'Вы уже оставляли отзыв этому организатору.')
        return redirect('organizer_detail', organizer_id=organizer.id)

    if request.method == 'POST':
        form = OrganizerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.organizer = organizer
            review.participant = request.user
            review.save()
            messages.success(request, 'Отзыв успешно добавлен.')
            return redirect('organizer_detail', organizer_id=organizer.id)
    else:
        form = OrganizerReviewForm()

    return render(request, 'events/organizer_detail.html', {
        'organizer': organizer,
        'review_form': form,
        'show_review_form': True,
        'events': Event.objects.filter(organizer=organizer).order_by('-date'),
        'events_count': Event.objects.filter(organizer=organizer).count(),
        'reviews': OrganizerReview.objects.filter(organizer=organizer).select_related('participant').order_by('-created_at'),
        'reviews_count': OrganizerReview.objects.filter(organizer=organizer).count(),
        'trust_rating': OrganizerReview.objects.filter(organizer=organizer).aggregate(avg=Avg('rating'))['avg'],
        'bonus_list': list(
            Event.objects.filter(organizer=organizer)
            .exclude(bonus_text='')
            .values_list('bonus_text', flat=True)
            .distinct()
        ),
        'existing_review': existing_review,
        'can_leave_review': True,
    })