from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from datetime import datetime, timedelta
import random

from users.forms import CustomUserCreationForm, TaskerSignUpForm, CustomUserChangeForm, TaskCreateForm, TaskDeleteForm, ScheduleCreateForm, SeekerSignUpForm, ToDoForm
from users.models import Tasker, TaskSeeker, CustomUser, TaskCanDo, Schedule, ToDo
from booking.models import ScheduleBooking, ScheduleBookingReview
from chat.models import Message
from .decorators import seeker_required, tasker_required

class SignUpView(generic.TemplateView):
    template_name = 'signup.html'

class SeekerSignUpView(generic.CreateView):
    form_class = SeekerSignUpForm
    template_name = 'registration/seeker_signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('user:profile_edit')

class TaskerSignUpView(generic.CreateView):
    form_class = TaskerSignUpForm
    template_name = 'registration/tasker_signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.add_message(self.request, messages.INFO, 'Please complete your registration!')
        return redirect('user:profile_edit')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Profile updated!')
            return redirect('user:profile_edit')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})

@user_passes_test(tasker_required)
@login_required
def tasks(request):
    tasks = TaskCanDo.objects.filter(tasker=request.user.id)

    if request.method == 'POST':
        form = TaskCreateForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.tasker = Tasker.objects.filter(user=request.user.id)[0]
            task.save()
    else:
        form = TaskCreateForm(user=request.user)


    return render(request, 'users/tasks.html', {'tasks': tasks,
                                                'form': form,
                                                })
@user_passes_test(tasker_required)
@login_required
def task_delete(request, _id):
    obj = TaskCanDo.objects.filter(id=_id, tasker=request.user.id)

    if request.method == 'POST':
        obj.delete()
    
    return redirect('user:tasks')

@user_passes_test(tasker_required)
@login_required
def tasker_schedule(request):
    schedule_list = Schedule.objects.filter(tasker=request.user.id)

    if request.method == 'POST':
        form = ScheduleCreateForm(request.POST, user=request.user)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.day_of_week = form.cleaned_data['day_of_week']
            schedule.start_time = form.cleaned_data['start_time']
            schedule.end_time = form.cleaned_data['end_time']
            schedule.tasker = Tasker.objects.filter(user=request.user.id)[0]

            schedule.save()
            messages.add_message(request, messages.SUCCESS, 'You added a new task!')
            return redirect('user:tasker-schedule')
    else:
        form = ScheduleCreateForm(user=request.user)

    return render(request, 'users/tasker_schedule.html', {'form': form, 'schedule_list': schedule_list})

@user_passes_test(tasker_required)
@login_required
def tasker_schedule_delete(request, _id):
    obj = Schedule.objects.get(id=_id, tasker=request.user.id)

    if request.method == 'POST':
        obj.delete()

    return redirect('user:tasker-schedule')

@login_required
def dashboard(request, todo_id=None):
    categories = TaskCanDo.TASK_CHOICES
    upcoming_tasks = None
    month_earnings = None
    todo_list = None
    form = None
    today = datetime.today()
    days_check = datetime.today() - timedelta(days=360)
    new_taskers = []
    unread_messages = None

    taskers_q = Tasker.objects.filter(user__date_joined__range=(days_check, today))
    rand_arr = random.sample(range(0,len(taskers_q)), 3)
    
    for i in range(0,3):
        new_taskers.append(taskers_q[rand_arr[i]])

    if request.user.is_tasker:
        upcoming_tasks = ScheduleBooking.objects.filter(tasker=request.user.tasker, completed=False, booking__range=(
                                                             datetime.today().strftime("%Y-%m-%d"), (datetime.today() + timedelta(days=30)) 
                                                             )).order_by('booking')[:3]
        month_earnings = ScheduleBooking.get_month_earnings(tasker=request.user.tasker)
        unread_messages = Message.get_unread_messages(id=request.user.id)

    if request.user.is_seeker:
        if request.method == 'POST':
            form = ToDoForm(request.POST)
            if form.is_valid():
                ToDo.objects.create(
                    seeker=request.user.taskseeker,
                    todo=form.cleaned_data['todo']
                )
                return redirect('user:dashboard')
        else:
            if todo_id:
                edit_todo = ToDo.objects.get(id=todo_id)
                form = ToDoForm(instance=edit_todo)
            else:
                form = ToDoForm()

        todo_list = ToDo.objects.filter(seeker=request.user.taskseeker)
        
    return render(request, 'dashboard.html', {'categories': categories, 
                                                'upcoming_tasks': upcoming_tasks, 
                                                'month_earnings': month_earnings, 
                                                'form': form, 
                                                'todo_list': todo_list,
                                                'new_taskers': new_taskers,
                                                'unread_messages': unread_messages
                                                })

@login_required
def todo_delete(request, id):
    obj = ToDo.objects.get(id=id, seeker=request.user.taskseeker)

    if request.method == 'POST':
        obj.delete()

    return redirect('user:dashboard')

@login_required
def tasker_profile_view(request, _id):
    tasker = Tasker.objects.filter(user=_id).first()
    task_can_do = TaskCanDo.objects.filter(tasker__user=_id)
    reviews = ScheduleBookingReview.objects.filter(schedule__tasker__user=_id)

    return render(request, 'users/tasker_profile.html', {'tasker': tasker, 
                                                        'task_can_do': task_can_do,
                                                        'reviews': reviews
                                                        })