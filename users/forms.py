from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Tasker, TaskSeeker, TaskCanDo, Schedule
from django import forms
from django.core.exceptions import ValidationError

from django.core.validators import RegexValidator

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = get_user_model()
        fields = ('username', 'email',)

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'address', 'language', 'nationality', 'bio', 'profile_picture', 'phone_num')

    def clean_phone_num(self):
        phone_num = self.cleaned_data['phone_num']
        regex = RegexValidator('^(0([1-9]{1}-?[1-9]\d{3}|[1-9]{2}-?\d{3}|[1-9]{2}\d{1}-?\d{2}|[1-9]{2}\d{2}-?\d{1})-?\d{4}|0[789]0-?\d{4}-?\d{4}|050-?\d{4}-?\d{4})$', 'Invalid phone number')
        if regex(phone_num) is not None:
            raise ValidationError('Invalid phone number')

        return phone_num


class TaskerSignUpForm(UserCreationForm):

    class Meta(UserCreationForm):
        
        model = get_user_model()
        fields = ('username', 'email',)

    def save(self):
        user = super().save(commit=False)
        user.is_tasker = True
        user.save()
        Tasker.objects.create(user=user)
        return user

class SeekerSignUpForm(UserCreationForm):

    class Meta(UserCreationForm):
        
        model = get_user_model()
        fields = ('username', 'email',)

    def save(self):
        user = super().save(commit=False)
        user.is_seeker = True
        user.save()
        TaskSeeker.objects.create(user=user)
        return user

class TaskCreateForm(forms.ModelForm):
    
    class Meta:
        model = TaskCanDo
        fields = ['category', 'description', 'price']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TaskCreateForm, self).__init__(*args,**kwargs)

    def clean_category(self):
        category = self.cleaned_data['category']
        tasks = TaskCanDo.objects.filter(tasker=self.user.id)
        
        for task in tasks:
            if category == task.category:
                raise ValidationError('You can only have one task type registered at a time')

        return category


class TaskDeleteForm(forms.ModelForm):

    class Meta:
        model = TaskCanDo
        fields = []

class ScheduleCreateForm(forms.ModelForm):

    class Meta:
        model = Schedule
        fields = ['day_of_week', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ScheduleCreateForm, self).__init__(*args,**kwargs)

    def clean(self):
        cleaned_data = super(ScheduleCreateForm, self).clean()
        start = cleaned_data.get('start_time', '')
        end = cleaned_data.get('end_time', '')

        if end < start:
            raise ValidationError('You can\'t have the end before the start!!')

        return cleaned_data

    def clean_day_of_week(self):
        qs = Schedule.objects.filter(tasker=self.user.id)
        day = self.cleaned_data['day_of_week']
        tasker_days = [day.day_of_week for day in qs]

        if day in tasker_days:
            raise ValidationError('You can only have one time slot for each day')

        return day

class ToDoForm(forms.Form):
    todo = forms.CharField(label="", max_length=150)