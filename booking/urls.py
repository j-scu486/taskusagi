from django.urls import path
from .views import booking_list, schedule_booking, available_times_ajax

urlpatterns = [
    path('booking_list/', booking_list, name="booking"),
    path('booking_schedule/<int:_id>', schedule_booking, name="schedule-booking"),
    path('booking_schedule/ajax/booking', available_times_ajax, name="booking-times"),
]