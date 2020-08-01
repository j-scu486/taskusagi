from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from datetime import datetime

from users.forms import CustomUserCreationForm, TaskerSignUpForm, CustomUserChangeForm, TaskCreateForm, TaskDeleteForm, ScheduleCreateForm, SeekerSignUpForm, ToDoForm
from users.models import Tasker, TaskSeeker, CustomUser, TaskCanDo, Schedule, ToDo
from booking.models import ScheduleBooking
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
        return redirect('user:profile_edit')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
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
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.tasker = Tasker.objects.filter(user=request.user.id)[0]
            task.save()
    else:
        form = TaskCreateForm()


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
    print(schedule_list)

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

    if request.user.is_tasker:
        upcoming_tasks = ScheduleBooking.objects.filter(tasker=request.user.tasker, booking__contains=datetime.today().strftime("%Y-%m-%d")).order_by('booking')[:3]
        month_earnings = ScheduleBooking.get_month_earnings()

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
        
    return render(request, 'dashboard.html', {'categories': categories, 'upcoming_tasks': upcoming_tasks, 'month_earnings': month_earnings, 'form': form, 'todo_list': todo_list})

@login_required
def todo_delete(request, id):
    obj = ToDo.objects.get(id=id, seeker=request.user.taskseeker)
    print(obj)

    if request.method == 'POST':
        obj.delete()

    return redirect('user:dashboard')
