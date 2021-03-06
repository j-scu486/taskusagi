from django.urls import path
from .views import SignUpView, SeekerSignUpView, TaskerSignUpView, edit_profile, tasks, task_delete, dashboard, tasker_schedule,tasker_schedule_delete,todo_delete, tasker_profile_view

app_name = 'user'

urlpatterns = [
    path('dashboard/', dashboard, name="dashboard"), 
    path('dashboard/<int:todo_id>/', dashboard, name="dashboard"), 
    path('signup/', SignUpView.as_view(), name='signup'),
    path('seeker_signup/', SeekerSignUpView.as_view(), name='seeker-signup'),
    path('tasker_signup/', TaskerSignUpView.as_view(), name='tasker-signup'),
    path('profile_edit/', edit_profile, name='profile_edit'),
    path('tasker_tasks/', tasks, name='tasks'),
    path('tasker_schedule/', tasker_schedule, name='tasker-schedule'),
    path('tasker_task_delete/<int:_id>', task_delete, name='task-delete'),
    path('tasker_schedule_delete/<int:_id>', tasker_schedule_delete, name='tasker-schedule-delete'),
    path('tasker_profile/<int:_id>', tasker_profile_view, name='tasker-profile'),
    path('todo_delete/<int:id>/', todo_delete, name='todo-delete')
]