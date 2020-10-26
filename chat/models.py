from django.db import models
from users.models import CustomUser
from booking.models import ScheduleBooking

class Message(models.Model):
    user_sent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    user_received = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    booking = models.ForeignKey(ScheduleBooking, on_delete=models.CASCADE)
    message_created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(max_length=200)
    message_read = models.BooleanField(default=False)

    @classmethod
    def get_messages(cls, booking):
        data = []
        booking_instance = cls.objects.filter(booking=booking).order_by('message_created')

        for item in booking_instance:
            data.append({
                'id': item.id,
                'sent': {
                    'id': item.user_sent.id,
                    'name': item.user_sent.get_full_name()
                },
                'received': {
                    'id': item.user_received.id,
                    'name': item.user_received.get_full_name()
                },
                'message': item.message,
                'created': item.message_created,
            })
        
        return data

    def __str__(self):
        return 'Message Instance | {} '.format(self.booking)
