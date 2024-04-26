import datetime
# from msilib.schema import SelfReg
from pyexpat.errors import messages

from django.http import JsonResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect, render
from django.views.generic import CreateView

from .forms import LoginForm, TimeSlotForm
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .decorators import student_required, teacher_required

from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *



from django.shortcuts import render
from django.http import HttpResponse

from xhtml2pdf import pisa
from django.template.loader import get_template

from .models import Booking


from .models import Subjects ,Student


from django.contrib.auth.decorators import login_required


@login_required
@student_required
def student_home(request):
   
    
    Students=Student.objects.all() 

    courseid=request.GET.get('course',None)
    subjectid=request.GET.get('subjects',None)
    slotid=request.GET.get('slot',None)
    subjects=None
    timeslot=None
    slot=None
    if courseid:
        getcourse=Course.objects.get(id=courseid)
        subjects=Subjects.objects.filter(course=getcourse)
    if subjectid:
        getsubjects=Subjects.objects.get(id=subjectid)
        timeslot=TimeSlot.objects.filter(subjects=getsubjects)
   
        
    if timeslot is None:
        teacher_names = []
    else:
        # Fetch all distinct teacher names associated with saved TimeSlot objects
        teacher_names = list(set(slot.teacher.first_name for slot in timeslot if slot.teacher is not None))
    
    
    
    course=Course.objects.all()
    students=Student.objects.all()

    current_student = Student.objects.get(user=request.user) 

    # Query all bookings for the current student
    student_bookings = Booking.objects.filter(student=current_student)
    remove_slot_id = request.POST.get('remove_slot')  # Use 'remove_slot' not 'remove_slot_id'
    
    if remove_slot_id:
        try:
            slot_to_remove = Booking.objects.get(id=remove_slot_id)
            if slot_to_remove.student.user == request.user:
                slot_to_remove.delete()
                messages.success(request, 'Slot removed successfully!')
                
        except Booking.DoesNotExist:  # Use 'Booking.DoesNotExist' instead of 'TimeSlot.DoesNotExist'
            pass  # Remove this line to prevent the error message
    remove_slot_id = request.POST.get('remove_slot')
    
    print(locals())
    print(student_bookings)

     
    return render(request, 'users/student_home.html',locals())

 



def book_slot(request, timeslot_id):
    student = request.user.student
    timeslot = get_object_or_404(TimeSlot, id=timeslot_id)

    # Check if the student has already booked the timeslot
    if Booking.objects.filter(student=student, timeslot=timeslot).exists():
        return JsonResponse({'success': False, 'message': 'You have already booked this timeslot.'})

    try:
        booking = Booking.objects.create(student=student, timeslot=timeslot)
        timeslot.booked_seats += 1
        timeslot.update_availability()
        booking.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})



from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Booking

def generate_pdf(request):
    # Get the current student
    current_student = Student.objects.get(user=request.user) 
    # Query all bookings for the current student
    student_bookings = Booking.objects.filter(student=current_student)

    template_path = 'users/student_home.html'  # Replace with the actual path of your template
    context = {'student_bookings': student_bookings}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_bookings.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error')

    return response


    

class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_student:
                return reverse('student-home')
            elif user.is_teacher:
                return reverse('teacher-home')
        else:
            return reverse('login')
    
 

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import TimeSlot, Teacher,Subjects, room

@login_required
def teacher_home(request):
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slot saved successfully!')

    weekdays = [day[1] for day in TimeSlot.WEEKDAY_CHOICES]
    start_hours = [hour[1] for hour in TimeSlot.START_HOUR_CHOICES]
    all_rooms = room.objects.all()

    teacher = Teacher.objects.all()

    booked_timeslots = TimeSlot.objects.all().values("weekday", "start_hour", "room")

    # Create a dictionary to store booked room ids by weekday and start_hour
    booked_rooms_by_slot = {}
    for timeslot in booked_timeslots:
        weekday = dict(TimeSlot.WEEKDAY_CHOICES)[timeslot['weekday']]
        start_hour = dict(TimeSlot.START_HOUR_CHOICES)[timeslot['start_hour']]
        room_id = timeslot['room']
        booked_rooms_by_slot.setdefault(weekday, {}).setdefault(start_hour, []).append(room_id)

    available_rooms_by_slot = {}
    for weekday in weekdays:
        for start_hour in start_hours:
            booked_rooms = booked_rooms_by_slot.get(weekday, {}).get(start_hour, [])
            available_rooms = [room for room in all_rooms if room.id not in booked_rooms]
            available_rooms_by_slot.setdefault(weekday, {}).setdefault(start_hour, available_rooms)

    timeslot = TimeSlot.objects.all()
    logged_in_teacher = Teacher.objects.get(user=request.user)

    booked_slots_by_teacher = TimeSlot.objects.filter(teacher=logged_in_teacher).values("weekday", "start_hour").distinct()

    booked_slots_dict = {}
    for slot in booked_slots_by_teacher:
        weekday = dict(TimeSlot.WEEKDAY_CHOICES)[slot["weekday"]]
        start_hour = dict(TimeSlot.START_HOUR_CHOICES)[slot["start_hour"]]
        booked_slots_dict.setdefault(weekday, {}).setdefault(start_hour, True)

    subjectss = Subjects.objects.all()

    remaining_subjects = []  # List to store subjects that haven't reached the limit

    for subject in subjectss:
        total_slots_booked = TimeSlot.objects.filter(subjects=subject).count()
        if total_slots_booked < subject.subj_count:  # Use subj_count field as the limit
            remaining_credits = subject.credits
            booked_slots = [slot for slot in timeslot if slot.subjects == subject and slot.teacher == logged_in_teacher]
            remaining_credits -= len(booked_slots)  # Subtract booked slots count
            subject.remaining_credits = remaining_credits  # Add remaining credits to the subject object
            remaining_subjects.append(subject)

    # Filter out subjects with remaining credits less than or equal to zero
    remaining_subjects = [subject for subject in remaining_subjects if subject.remaining_credits > 0]

    context = {
        'weekdays': weekdays,
        'start_hours': start_hours,
        'available_rooms_by_slot': available_rooms_by_slot,
        'subjectss': remaining_subjects,  # Use the filtered list of remaining subjects
        'teacher': teacher,
        'logged_in_teacher': logged_in_teacher,
        'timeslot': timeslot,
        'booked_slots_dict': booked_slots_dict,
    }

    remove_slot_id = request.POST.get('remove_slot')

    if remove_slot_id:
        try:
            slot_to_remove = TimeSlot.objects.get(id=remove_slot_id)
            if slot_to_remove.teacher.user == request.user:
                slot_to_remove.delete()
                messages.success(request, 'Slot removed successfully!')
                return redirect('teacher_home')
        except TimeSlot.DoesNotExist:
            pass  # Remove this line to prevent the error message

    context['refresh_page'] = True

    return render(request, 'index.html', context)




from django.views.decorators.csrf import csrf_protect
import json
@csrf_protect
def handle_slot_booking(request):
    if request.method == 'POST':
        post_data = json.loads(request.body)

        weekday = {time: hour for hour, time in TimeSlot.WEEKDAY_CHOICES}
        time_to_hour = {time: hour for hour, time in TimeSlot.START_HOUR_CHOICES}

        print('============  ',post_data)
        
        # Create a new TimeSlot instance with the selected data
        try:
            timeslot = TimeSlot(
                room_id = post_data.get('roomID'),
                weekday = weekday.get(
                    post_data.get('weekday')
                ),
                start_hour = time_to_hour.get(
                    post_data.get('start_hour')
                ),
                subjects_id = int(post_data.get('subject')),
                teacher = request.user.teacher,
            )

            # Save the TimeSlot instance to the database
            timeslot.save()

            # Update availability status after saving the timeslot
            timeslot.update_availability()

            

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request.'})


