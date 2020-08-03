from django import forms
from .models import ScheduleBooking, ScheduleBookingReview

class ScheduleBookingForm(forms.ModelForm):
    booking = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])

    class Meta:
        model = ScheduleBooking
        fields = ['booking', 'notes',]

class ScheduleBookingReviewForm(forms.ModelForm):

    class Meta:
        model = ScheduleBookingReview
        fields = ['review', 'completed', 'rating']

    def clean_completed(self):
        completed = self.cleaned_data['completed']
        if completed is False:
            raise forms.ValidationError('Please mark this schedule as completed in order to leave a review')

        return completed