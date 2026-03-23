from django import forms
from .models import Event, OrganizerReview


class EventForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Дата и время'
    )

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'date',
            'direction',
            'base_points',
            'difficulty_coef',
            'bonus_text',
            'max_participants',
        ]


class OrganizerReviewForm(forms.ModelForm):
    class Meta:
        model = OrganizerReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }