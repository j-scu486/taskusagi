from django.urls import path
from .views import booking_list, schedule_booking, available_times_ajax, booking_search, booking_detail, tasker_reviews_ajax

app_name = 'booking'

urlpatterns = [
    path('booking_list/<int:_id>', booking_list, name="booking-list"),
    path('booking_search/<slug:category>', booking_search, name="booking-search"),
    path('booking_schedule/<int:_id>/<str:category>/', schedule_booking, name="schedule-booking"),
    path('booking_schedule/<int:_id>/<str:category>/ajax/booking', available_times_ajax, name="booking-times"),
    path('booking_detail/<int:id>/', booking_detail, name="booking-detail"),
    path('booking_search/ajax/reviews/<int:_id>/', tasker_reviews_ajax, name="tasker-reviews")
]