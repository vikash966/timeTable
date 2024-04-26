from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import views




urlpatterns = [
    path("", views.student_home, name="student-home"),
    path("teacher/", views.teacher_home, name="teacher-home"),
    path("login/", views.LoginView.as_view(), name="login"),

    path('logout/', auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),
    path('book-slot/', views.book_slot, name='book_slot'),
    path('ussers/student_home/ussers/student_home/', views.student_home, name='student_home'),
    path('book_slot/<int:timeslot_id>/', views.book_slot, name='book_slot_slot_id'),
    
    path('teacher_home/', views.teacher_home, name='teacher_home'),

    path('handle_slot_booking/', views.handle_slot_booking, name='handle_slot_booking'),
    path('download-pdf/', views.generate_pdf, name='download_pdf'),
    

  




    
   
]


    
     