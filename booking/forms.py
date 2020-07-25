from django.forms import forms, ModelForm
from django.forms import DateTimeField
from .models import ScheduleBooking

class ScheduleBookingForm(ModelForm):
    booking = DateTimeField(input_formats=['%d/%m/%Y %H:%M'])

    class Meta:
        model = ScheduleBooking
        fields = ['booking', 'notes',]