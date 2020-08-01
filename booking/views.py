from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse

from users.models import Schedule, TaskCanDo, Tasker, TaskSeeker
from users.decorators import seeker_required, tasker_required
from booking.models import ScheduleBooking
from booking.forms import ScheduleBookingForm, ScheduleBookingComplete
from .ratings import r

def booking_detail(request, id):
    booking = ScheduleBooking.objects.get(id=id)

    if request.method == 'POST':
        form = ScheduleBookingComplete(request.POST)
        if form.is_valid():
            booking.completed = form.cleaned_data['completed']
            booking.save()

            form_rating = form.cleaned_data['rating']
            rating_count = r.incr('tasker:{}:recom_count'.format(booking.tasker.user.id))
            rating = r.incr('tasker:{}:recom_total'.format(booking.tasker.user.id), amount=form_rating)
            r.incr('tasker:{}:completed_tasks'.format(booking.tasker.user.id))
            
            tasker = Tasker.objects.get(user=booking.tasker.user.id)
            tasker.rating = (rating / rating_count)
            tasker.save()
            
            messages.add_message(request, messages.SUCCESS, 'Thanks for reviewing your tasker!')
            return redirect(reverse('booking:booking-list', kwargs={'_id': request.user.id}))
    else:
        form = ScheduleBookingComplete

    return render(request, 'booking/booking_detail.html', {'booking': booking, 'form': form})

def booking_list(request, _id):
    bookings = None

    if request.user.is_tasker:
        bookings = ScheduleBooking.objects.filter(tasker=_id)
    else:
        bookings = ScheduleBooking.objects.filter(seeker=_id)

    bookings = bookings.order_by('-booking')

    return render(request, 'booking/booking_list.html', {'bookings': bookings})

def booking_search(request, category):
    results = TaskCanDo.objects.filter(category=category)
    category_name = results[0].catagory_display() if results else None

    price = request.GET.get('price')
    results = results.order_by('-price') if price == 'high' else results.order_by('price')

    return render(request, 'booking/booking_search.html', {'results': results, 'category_name': category_name})

def schedule_booking(request, _id, category):
    day_arr = Schedule.get_unavailable_days(_id)
    form_cat = None

    for cat in TaskCanDo.TASK_CHOICES:
        if category in cat:
            form_cat = cat[1]

    if request.method == 'POST':
        form = ScheduleBookingForm(request.POST)
        if form.is_valid():
            # Create a new booking
            booking = form.save(commit=False)
            tasker = Tasker.objects.get(user=_id)
            seeker = TaskSeeker.objects.get(user=request.user.id)

            booking.category = form_cat
            booking.tasker = tasker
            booking.seeker = seeker
            booking.price = TaskCanDo.objects.filter(tasker=tasker).first().price

            booking.save()
            # Create a new message instance and set up
            
            messages.add_message(request, messages.SUCCESS, 'You\'re all set!')
            return redirect(reverse('booking:booking-list', kwargs={'_id': request.user.id}))
    else:
        form = ScheduleBookingForm()

    return render(request, 'booking/booking.html', {'form': form, 'day_arr': day_arr, 'user_id': _id})

# Ajax request to get array of available times dynamically
def available_times_ajax(request, _id, category):
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