from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse

from users.models import Schedule, TaskCanDo, Tasker, TaskSeeker
from users.decorators import seeker_required, tasker_required
from booking.models import ScheduleBooking, ScheduleBookingReview
from booking.forms import ScheduleBookingForm, ScheduleBookingReviewForm
from .ratings import r
import datetime

def booking_detail(request, id):
    booking = ScheduleBooking.objects.get(id=id)

    if request.method == 'POST':
        form = ScheduleBookingReviewForm(request.POST)
        if form.is_valid():
            booking_review = form.save(commit=False)
            booking_review.schedule = booking
            booking.completed = True
            booking.save()
            booking_review.save()

            # Update redis 
            form_rating = form.cleaned_data['rating']
            rating_count = r.incr('tasker:{}:recom_count'.format(booking.tasker.user.id))
            rating = r.incr('tasker:{}:recom_total'.format(booking.tasker.user.id), amount=form_rating)
            r.incr('tasker:{}:completed_tasks'.format(booking.tasker.user.id))
            
            # Calculate and set tasker review rating and add to completed tasks
            tasker = Tasker.objects.get(user=booking.tasker.user.id)
            tasker.rating = (rating / rating_count)
            tasker.completed += 1
            tasker.save()
            
            messages.add_message(request, messages.SUCCESS, 'Thanks for reviewing your tasker!')
            return redirect(reverse('booking:booking-list', kwargs={'_id': request.user.id}))
    else:
        form = ScheduleBookingReviewForm

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
    time_pref = request.GET.get('task-time')
    price = request.GET.get('price')

    time_morning_1 = datetime.time(9,0,0)
    time_morning_2 = datetime.time(12,0,0)

    time_afternoon_1 = datetime.time(12,0,0)
    time_afternoon_2 = datetime.time(17,0,0)

    time_evening_1 = datetime.time(15,0,0)
    time_evening_2 = datetime.time(20,0,0)

    if time_pref == 'morning':
        results = results.filter(tasker__schedule__start_time__range=(time_morning_1, time_morning_2)).distinct()
    elif time_pref == 'afternoon':
        results = results.filter(tasker__schedule__start_time__range=(time_afternoon_1, time_afternoon_2)).distinct()
    elif time_pref == 'evening':
        results = results.filter(tasker__schedule__start_time__range=(time_evening_1, time_evening_2)).distinct()
    else:
        pass

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

def tasker_reviews_ajax(request, _id):
    reviews = ScheduleBookingReview.objects.filter(schedule__tasker__user=_id)[:5]
    data = []

    for review in reviews:
        seeker = TaskSeeker.objects.get(user_id=review.schedule.seeker.user.id)
        picture = None

        try:
            picture = seeker.user.profile_picture.url
        except ValueError:
            picture = 'https://lh3.googleusercontent.com/proxy/1Ns5bl_A4oo3EiBoDQRXYoBQp8CwKzUPztOH-1LoQ1Y9Fq_Kh_MAWAPVHPM0ohlT4qPxuDAxYJRjkdloaqluDRs28c4DTzZKUlNH3XY'
            
        data.append({
            'id': review.id,
            'review': review.review,
            'created': review.created.strftime("%B %w, %Y"),
            'rating': review.rating,
            'seeker': seeker.user.first_name,
            'profile_url': picture
        })
    
    return JsonResponse({'data': data, 'user_id': _id })