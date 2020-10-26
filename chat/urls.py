from django.urls import path
from .views import messages, messages_json, send_message_json

app_name = 'chat'

urlpatterns = [
    path('<int:booking_id>', messages, name="my-messages"), 
    path('messages/json/<int:booking_id>', messages_json, name="json-messages"),
    path('messages/json/send_message/<int:booking_id>', send_message_json, name="messages-send")

]