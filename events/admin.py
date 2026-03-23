from django.contrib import admin
from .models import Event, EventParticipation, OrganizerReview


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'organizer',
        'direction',
        'date',
        'base_points',
        'difficulty_coef',
        'final_points',
        'participants_count',
    )
    list_filter = ('direction', 'date', 'organizer')
    search_fields = ('title', 'description', 'organizer__username', 'organizer__full_name')
    ordering = ('-date',)

    @admin.display(description='Итоговые баллы')
    def final_points(self, obj):
        return obj.calculated_points()

    @admin.display(description='Участников')
    def participants_count(self, obj):
        return obj.participations.count()


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event',
        'participant',
        'status',
        'earned_points',
        'confirmed_by',
        'confirmed_at',
    )
    list_filter = ('status', 'event', 'confirmed_by')
    search_fields = ('event__title', 'participant__username', 'participant__full_name')
    ordering = ('-created_at',)

    actions = ['mark_as_confirmed']

    @admin.action(description='Подтвердить выбранные участия и начислить баллы')
    def mark_as_confirmed(self, request, queryset):
        updated_count = 0

        for participation in queryset:
            if participation.status != 'confirmed':
                participation.status = 'confirmed'
                participation.earned_points = participation.event.calculated_points()
                participation.confirmed_by = request.user
                participation.save()
                updated_count += 1

        self.message_user(request, f'Подтверждено участий: {updated_count}')


@admin.register(OrganizerReview)
class OrganizerReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'organizer',
        'participant',
        'rating',
        'short_comment',
        'created_at',
    )
    list_filter = ('rating', 'created_at', 'organizer')
    search_fields = (
        'organizer__username',
        'organizer__full_name',
        'participant__username',
        'participant__full_name',
        'comment',
    )
    ordering = ('-created_at',)

    @admin.display(description='Комментарий')
    def short_comment(self, obj):
        if obj.comment:
            return obj.comment[:50]
        return '—'