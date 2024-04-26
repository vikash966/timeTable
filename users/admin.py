
# Register your models here.
from django.contrib import admin
from .models import User, Student, Teacher  , TimeSlot ,room , Subjects ,Course ,Booking,Profile



admin.site.register(Profile)

admin.site.register(User)

admin.site.register(Student)
admin.site.register(Teacher)

admin.site.register(TimeSlot)
admin.site.register(room)
admin.site.register(Subjects)
admin.site.register(Course)
admin.site.register(Booking)
