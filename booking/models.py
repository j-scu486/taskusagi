import functools
from django.db import models
from django.core import serializers
from users.models import Tasker, TaskSeeker
from django.urls import reverse
from datetime import datetime


class ScheduleBooking(models.Model):
    tasker = models.ForeignKey('users.Tasker', on_delete=models.CASCADE)
    seeker = models.ForeignKey('users.TaskSeeker', on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    booking = models.DateTimeField()
    price = models.IntegerField()
    notes = models.TextField(max_length=200)
    completed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('booking:booking-detail', kwargs={'id': self.id })

    @classmethod
    def get_bookings(cls, _id, date):
        test = cls.objects.filter(tasker=_id, booking__date=date)
        bookings_dict = []
        
        for item in test:
            bookings_dict.append(item.booking.time().strftime("%H:%M"))

        return bookings_dict

    @classmethod
    def get_month_earnings(cls):
        current_month_schedules = cls.objects.filter(booking__month=datetime.today().month)
        bookings_list = []
        for booking in current_month_schedules:
            bookings_list.append(booking.price)
            
        return functools.reduce(lambda a,b: a+b, bookings_list) if len(bookings_list) else 0

    def __str__(self):
        return 'Tasker: {}, Seeker: {}, Booking: {}'.format(self.tasker, self.seeker, self.booking)