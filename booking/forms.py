from django import forms
from .models import ScheduleBooking

class ScheduleBookingForm(forms.ModelForm):
    booking = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])

    class Meta:
        model = ScheduleBooking
        fields = ['booking', 'notes',]

choices = [
    ('1', 1),
    ('2', 2),
    ('3', 3),
    ('4', 4),
    ('5', 5)
]

class ScheduleBookingComplete(forms.Form):
    completed = forms.BooleanField(required=False)
    rating = forms.ChoiceField(choices=choices)


