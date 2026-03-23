from django.urls import path
from .views import (
    event_list_view,
    event_detail_view,
    event_create_view,
    event_update_view,
    register_for_event_view,
    my_events_view,
    organizer_event_participants_view,
    confirm_participation_view,
    organizer_detail_view,
    add_organizer_review_view,
    checkin_by_qr_view,
)

urlpatterns = [
    path('', event_list_view, name='event_list'),
    path('create/', event_create_view, name='event_create'),
    path('my/', my_events_view, name='my_events'),
    path('checkin/<uuid:token>/', checkin_by_qr_view, name='checkin_by_qr'),
    path('organizer/<int:organizer_id>/', organizer_detail_view, name='organizer_detail'),
    path('organizer/<int:organizer_id>/review/', add_organizer_review_view, name='add_organizer_review'),
    path('<int:event_id>/', event_detail_view, name='event_detail'),
    path('<int:event_id>/edit/', event_update_view, name='event_update'),
    path('<int:event_id>/register/', register_for_event_view, name='register_for_event'),
    path('<int:event_id>/participants/', organizer_event_participants_view, name='organizer_event_participants'),
    path('participation/<int:participation_id>/confirm/', confirm_participation_view, name='confirm_participation'),
]