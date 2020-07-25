from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Tasker, TaskSeeker, TaskCanDo, Schedule

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), 
        {'fields': 
            ('first_name', 'last_name', 'email', 'address', 'language', 'nationality', 'bio', 'is_seeker', 'is_tasker', 'profile_picture', 'phone_num')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'address', 'password1', 'password2')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Tasker)
admin.site.register(TaskSeeker)
admin.site.register(Schedule)
admin.site.register(TaskCanDo)