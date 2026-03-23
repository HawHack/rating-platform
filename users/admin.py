from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'role',
        'city',
        'age',
        'direction',
        'is_approved_organizer',
        'organized_events_count',
        'is_staff',
    )

    list_filter = (
        'role',
        'direction',
        'city',
        'is_approved_organizer',
        'is_staff',
    )

    search_fields = ('username', 'full_name', 'email', 'city')
    ordering = ('id',)

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'full_name',
                'role',
                'city',
                'age',
                'direction',
                'is_approved_organizer',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'full_name',
                'role',
                'city',
                'age',
                'direction',
                'is_approved_organizer',
            )
        }),
    )

    actions = ['approve_organizers', 'remove_organizer_approval']

    @admin.display(description='Кол-во мероприятий')
    def organized_events_count(self, obj):
        return obj.organized_events.count()

    @admin.action(description='Одобрить выбранных организаторов')
    def approve_organizers(self, request, queryset):
        updated = queryset.filter(role='organizer').update(is_approved_organizer=True)
        self.message_user(request, f'Одобрено организаторов: {updated}')

    @admin.action(description='Снять одобрение с выбранных организаторов')
    def remove_organizer_approval(self, request, queryset):
        updated = queryset.filter(role='organizer').update(is_approved_organizer=False)
        self.message_user(request, f'Снято одобрение у организаторов: {updated}')