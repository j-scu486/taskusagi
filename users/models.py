from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date, datetime, time, timedelta

# https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html

class CustomUser(AbstractUser):

    JAPANESE = 'JP'
    ENGLISH = 'EN'

    LANGUAGE_CHOICES = [
        (JAPANESE, 'Japanese'),
        (ENGLISH, 'English'),
    ]
    
    address = models.CharField(max_length=100)
    language= models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default=ENGLISH,
    )
    nationality = models.CharField(max_length=100)
    bio = models.TextField(max_length=200)
    profile_picture = models.ImageField(upload_to='users/', blank=True)
    phone_num = models.CharField(max_length=11)
    is_tasker = models.BooleanField(default=False)
    is_seeker = models.BooleanField(default=False)
    # Notifications to be added later
    
class TaskSeeker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)

class Tasker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)

class Schedule(models.Model):

    MONDAY = 'MON'
    TUESDAY = 'TUE'
    WEDNESDAY = 'WED'
    THURSDAY = 'THU'
    FRIDAY = 'FRI'
    SATURDAY = 'SAT'
    SUNDAY = 'SUN'

    DAY_CHOICES = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    ]    

    tasker = models.ForeignKey('Tasker', on_delete=models.CASCADE)
    day_of_week = models.CharField(
        max_length=3,
        choices=DAY_CHOICES,
        default=MONDAY,
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    @classmethod
    def get_unavailable_days(cls, _id):
        schedule_list = cls.objects.filter(tasker=_id)

        day_dict = {'SUN': 0,'MON': 1,'TUE': 2,'WED': 3,'THU': 4,'FRI': 5,'SAT': 6}
        day_arr = [0,1,2,3,4,5,6]

        for day in schedule_list:
            if day.day_of_week in day_dict:
                day_arr.remove(day_dict[day.day_of_week])
        
        return day_arr

    def time_array(self):
        time_arr = [self.start_time.strftime("%H:%M")]

        def to_time(time):
            if time != self.end_time:
                dt = datetime.combine(date.today(), time) + timedelta(minutes=30)
                time_arr.append(dt.time().strftime("%H:%M"))
                to_time(dt.time())
            else:
                return

        to_time(self.start_time)
        return time_arr

    def __str__(self):
        return '{}: {}, {}'.format(self.get_day_of_week_display(), self.start_time, self.end_time)

class TaskCanDo(models.Model):


    MOVING = 'MOV'
    REPAIRS = 'REP'
    PLUMBING = 'PLM'
    CLEANING = 'CLN'
    DELIVERY = 'DLV'

    TASK_CHOICES = [
        (MOVING, 'Moving'),
        (REPAIRS, 'Home Repairs'),
        (PLUMBING, 'Plumbing'),
        (CLEANING, 'Cleaning'),
        (DELIVERY, 'Delivery'),
    ]    

    tasker = models.ForeignKey('Tasker', on_delete=models.CASCADE)
    category = models.CharField(
        max_length=3,
        choices=TASK_CHOICES,
        default=CLEANING,
    )    
    description = models.TextField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return '{} | {}'.format(self.tasker, self.get_category_display())
