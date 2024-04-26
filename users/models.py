# Create your models here
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.


class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Subjects(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    credits=models.IntegerField()
    subj_count=models.IntegerField()

    



    def __str__(self):
        return self.name

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    batch = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=100)
    sapid = models.CharField(max_length=9, unique=True, default='00000000')


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='teacher')
    first_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    sapid = models.CharField(max_length=9, unique=True, default='00000000')
















class room(models.Model):
    roomno = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.roomno} (Capacity: {self.capacity})"



class TimeSlot(models.Model):
    WEEKDAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
    )
    START_HOUR_CHOICES = (
        (8, '8 AM'),
        (9, '9 AM'),
        (10, '10 AM'),
        (11, '11 AM'),
        (12, '12 PM'),
        (13, '1 PM'),
        (14, '2 PM'),
        (15, '3 PM'),
        (16, '4 PM'),
        (17, '5 PM'),
    )
   

    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_hour = models.IntegerField(choices=START_HOUR_CHOICES)
    subjects = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room = models.ForeignKey(room, on_delete=models.CASCADE)
    booked_seats = models.IntegerField(blank=True, null=True)  # New field to track the number of booked seats
    is_booked = models.BooleanField(default=False, blank=True)
    
    def __str__(self):
        return f"{self.get_weekday_display()} {self.get_start_hour_display()} - Room: {self.room.roomno} (Capacity: {self.room.capacity})"

    # New method to check if the timeslot has available seats
    def has_available_seats(self):
        return self.room.capacity > self.booked_seats
    
    def update_availability(self):
        booked_seats = TimeSlot.objects.filter(weekday=self.weekday, start_hour=self.start_hour, room=self.room).count()
        self.booked_seats = booked_seats
        if booked_seats >= self.room.capacity:
            self.is_booked = True
        else:
            self.is_booked = False
            
            self.save()

        

    class Meta:
        unique_together = ('weekday', 'start_hour', 'room')

    
    


   

class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    sapid = models.CharField(max_length=9, blank=True, null=True)  # Add sapid field to Booking model
    is_booked = models.BooleanField(default=False)  # New field to indicate if the seat is booked

    def __str__(self):
        return f"{self.student.user.username} - {self.timeslot}"

    class Meta:
        # Add a unique constraint to prevent duplicate bookings for the same student and timeslot
        unique_together = ('student', 'timeslot')

    def save(self, *args, **kwargs):
        # Automatically save the sapid of the student when a booking is made
        if not self.sapid:
            self.sapid = self.student.sapid

        # Check if the timeslot has available seats before making a booking
        if not self.timeslot.has_available_seats():
            raise Exception("No available seats for this timeslot.")

        # Increase booked_seats count when a new booking is made
        if not self.pk:
            self.timeslot.booked_seats += 1
            self.timeslot.update_availability()

        super(Booking, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Decrease booked_seats count when a booking is removed
        if self.pk:
            self.timeslot.booked_seats -= 1
            self.timeslot.update_availability()

        super(Booking, self).delete(*args, **kwargs)

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='Profile')
    image=models.ImageField(upload_to='pics',default='default.svg')
    def __str__(self):
        return f'{self.user} Profile'
