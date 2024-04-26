from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from .models import User, Student, Teacher ,room
from django import forms
from django.contrib.auth import get_user_model


from django import forms
from .models import TimeSlot


User = get_user_model()



    
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())




from django.db.models import Q

from django import forms
from .models import TimeSlot



from django import forms
from .models import TimeSlot

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['subjects', 'teacher', 'room', 'weekday', 'start_hour']
        widgets = {
            'teacher': forms.HiddenInput(),
            'booked_seats': forms.HiddenInput(),
            'is_booked': forms.HiddenInput(),
        }