from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from .forms import CustomUserCreationForm, TaskerSignUpForm, CustomUserChangeForm, TaskCreateForm, TaskDeleteForm, ScheduleCreateForm
from .models import Tasker, TaskSeeker, CustomUser, TaskCanDo, Schedule
from .decorators import seeker_required, tasker_required

class SignUpView(generic.TemplateView):
    template_name = 'signup.html'

class SeekerSignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/seeker_signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('profile_edit')

class TaskerSignUpView(generic.CreateView):
    form_class = TaskerSignUpForm
    template_name = 'registration/tasker_signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('profile_edit')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Update fields as necessary, redirect to dashboard page with success message
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse('All good!')
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
    
    return redirect('tasks')

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
            return redirect('tasker-schedule')
    else:
        form = ScheduleCreateForm(user=request.user)

    return render(request, 'users/tasker_schedule.html', {'form': form, 'schedule_list': schedule_list})

@user_passes_test(tasker_required)
@login_required
def tasker_schedule_delete(request, _id):
    obj = Schedule.objects.get(id=_id, tasker=request.user.id)

    if request.method == 'POST':
        obj.delete()

    return redirect('tasker-schedule')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')