from django.shortcuts import render, HttpResponse, redirect
from booking.models import ScheduleBooking
from django.http import HttpResponseForbidden


def sender_or_receiver(func):
    def wrapper(request, *args, **kwargs):  
        # Get booking id from kwargs and find relevant booking
        booking = ScheduleBooking.objects.get(id=kwargs['booking_id'])
        # Get ids of tasker and seeker
        # If request.id does not equal either tasker or seeker, abort 403
        if booking.tasker.user.id is not request.user.id and booking.seeker.user.id is not request.user.id:
            return HttpResponseForbidden('Forbidden: 403')
        return func(request, *args, **kwargs)

    return wrapper
