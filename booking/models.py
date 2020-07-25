from django.db import models
from django.core import serializers
from users.models import Tasker, TaskSeeker
import json

class ScheduleBooking(models.Model):
    tasker = models.ForeignKey('users.Tasker', on_delete=models.CASCADE)
    seeker = models.ForeignKey('users.TaskSeeker', on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    booking = models.DateTimeField()
    price = models.IntegerField()
    notes = models.TextField(max_length=200)

    @classmethod
    def get_bookings(cls, _id, date):
        test = cls.objects.filter(tasker=_id, booking__date=date)
        bookings_dict = []
        
        for item in test:
            bookings_dict.append(item.booking.time().strftime("%H:%M"))

        return bookings_dict

    def __str__(self):
        return 'Tasker: {}, Seeker: {}, Booking: {}'.format(self.tasker, self.seeker, self.booking)
    
    # Create a method to get all booked schedules for a tasker