from django import forms
from .models import Message

class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=100, required=False)
    