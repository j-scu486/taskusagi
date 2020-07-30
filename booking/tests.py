from django.test import TestCase, RequestFactory, Client
from users.models import CustomUser, TaskSeeker, Tasker, Schedule, TaskCanDo
from booking.models import ScheduleBooking

from booking.views import schedule_booking
from booking.forms import ScheduleBookingForm
from datetime import datetime

# User Tests

class UserTestCase(TestCase):
    def setUp(self):

        self.factory = RequestFactory()
        CustomUser.objects.create(
            username="Tasker1",
            first_name="Tasker",
            last_name="Tester",
            email="test@test.com",
            password="defragment",
            address="Test Street",
            bio="Test Bio",
            phone_num="08078303090",
            is_tasker=True
        )

        CustomUser.objects.create(
            username="Seeker1",
            first_name="Seeker",
            last_name="Tester",
            email="test2@test.com",
            password="defragment",
            address="Test Street 2",
            bio="Test Bio 2",
            phone_num="08078303091",
            is_seeker=True
        )

        CustomUser.objects.create(
            username="Seeker2",
            first_name="Seeker2",
            last_name="Tester",
            email="test3@test.com",
            password="defragment",
            address="Test Street 3",
            bio="Test Bio 3",
            phone_num="08078303091",
            is_seeker=True
        )

        Tasker.objects.create(user=CustomUser.objects.get(id=1))
        TaskSeeker.objects.create(user=CustomUser.objects.get(id=2))
        TaskSeeker.objects.create(user=CustomUser.objects.get(id=3))

        Schedule.objects.create(
            tasker=Tasker.objects.get(user=1),
            day_of_week='TUE',
            start_time="12:00",
            end_time="15:00"
        )

        TaskCanDo.objects.create(
            tasker=Tasker.objects.get(user=1),
            category='CLN',
            description='None',
            price='2000'
        )


    def test_schedule_unavailable_days(self):
        """
        Check that unavailable day array is returned correctly
        """
        schedule = Schedule.objects.filter(tasker=1).first()
        self.assertTrue(schedule)

        self.assertEqual(schedule.get_unavailable_days(_id=1), [0,1,3,4,5,6])
        schedule.day_of_week='SUN'
        schedule.save()
        schedule.refresh_from_db()
        self.assertEqual(schedule.get_unavailable_days(_id=1), [1,2,3,4,5,6])
        schedule.day_of_week='FRI'
        schedule.save()
        schedule.refresh_from_db()
        self.assertEqual(schedule.get_unavailable_days(_id=1), [0,1,2,3,4,6])

    def test_booking_post(self):
        """
        Test that schedules can be sucessfully booked
        """
        c = Client()

        seeker1 = TaskSeeker.objects.get(user=2)
        seeker2 = TaskSeeker.objects.get(user=3)
        self.assertTrue(seeker1)
        self.assertTrue(seeker2)

        book_schedule = c.post('/bookings/booking_schedule/1/CLN/', data=
            {'tasker': Tasker.objects.get(user=1),
             'seeker': seeker1,
             'category': 'CLN',
             'booking': datetime.now(),
             'price': 2000,
             'notes': "None",
             'completed': False
             }
            
        )
        self.assertEqual(book_schedule.status_code, 200)
        
    def test_booking_double_booking(self):
        """
        FALSE if a seeker tries to book a booking in a time slot that has a booking
        """
        c = Client()

        seeker1 = TaskSeeker.objects.get(user=2)
        seeker2 = TaskSeeker.objects.get(user=3)
        






