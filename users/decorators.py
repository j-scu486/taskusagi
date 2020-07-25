from django.contrib.auth.decorators import user_passes_test

def seeker_required(user):
    return user.is_seeker

def tasker_required(user):
    return user.is_tasker