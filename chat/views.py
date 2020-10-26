from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from booking.models import ScheduleBooking
from users.models import CustomUser
from .models import Message
from .forms import MessageForm
from .decorators import sender_or_receiver
import json

@sender_or_receiver
def messages(request, booking_id):
    form = MessageForm()
    booking = ScheduleBooking.objects.get(id=booking_id)
    messages = Message.get_messages(booking=booking)
    receiver_id = booking.seeker.user.id if request.user.id == booking.tasker.user.id else booking.tasker.user.id
    contact_list = None 

    if booking.message_set.latest('message_created').user_received == request.user:
        instance = booking.message_set.latest('message_created')
        instance.message_read=True
        instance.save()

    if request.user.is_tasker:
        contact_list = ScheduleBooking.objects.filter(tasker=request.user.id)
    else:
        contact_list = ScheduleBooking.objects.filter(seeker=request.user.id)

    return render(request, 'chat/my_messages.html', {'booking_id': booking_id, 
                                                    'form': form,
                                                    'receiver_id': receiver_id,
                                                    'contact_list': contact_list
                                                    })

@sender_or_receiver
def messages_json(request, booking_id):
    booking = ScheduleBooking.objects.get(id=booking_id)
    messages = Message.get_messages(booking=booking)

    return JsonResponse(messages, safe=False)

@sender_or_receiver
def send_message_json(request, booking_id):
    booking = ScheduleBooking.objects.get(id=booking_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            data = json.loads(request.body)
            Message.objects.create(
                    user_sent=request.user, 
                    user_received=CustomUser.objects.get(id=data['receiver_id']),
                    booking=booking,
                    message=data['message']
            )
            return JsonResponse(data, safe=False)
    
    return JsonResponse({}, safe=False)
