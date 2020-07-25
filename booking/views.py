from django.shortcuts import render, HttpResponse
from .forms import ScheduleBookingForm
from django.http import JsonResponse

from users.models import Schedule
from booking.models import ScheduleBooking

def booking_list(request):
    # View all scheduled bookings (listview)

    return render(request, 'booking/booking_list.html')

def schedule_booking(request, _id):
    # Pull data to show tasker info and add this to form instance
    day_arr = Schedule.get_unavailable_days(_id)

    if request.method == 'POST':
        form = ScheduleBookingForm(request.POST)
        if form.is_valid():
            return HttpResponse('Submitted!')
    else:
        form = ScheduleBookingForm()

    return render(request, 'booking/booking.html', {'form': form, 'day_arr': day_arr, 'user_id': _id})

# Ajax request to get array of available times dynamically
def available_times_ajax(request):
    day = int(request.GET.get('booking', None))
    user = request.GET.get('user', None)
    date = request.GET.get('date', None)

    day_dict = {0: 'SUN', 1: 'MON', 2: 'TUE', 3: 'WED', 4: 'THU', 5: 'FRI', 6: 'SAT'}
    available_times_arr = []
    booked_arr = []
    
    tasker_schedule = Schedule.objects.filter(day_of_week=day_dict[day]).first()
    tasker_booking = ScheduleBooking.objects.filter(tasker=user).first()

    if tasker_schedule is not None:
        available_times_arr = tasker_schedule.time_array()

    if tasker_booking is not None:
        booked_arr = tasker_booking.get_bookings(user, date)

    data = {
        'available': available_times_arr,   
        'booked': booked_arr,
    }

    return JsonResponse(data)