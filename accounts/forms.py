# from django import forms
# from django.contrib.auth.models import User
# from .models import Profile

# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email']

# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['age', 'weight', 'height', 'unit_preference']
#         widgets = {
#             'unit_preference': forms.HiddenInput(),
#         }

from django import forms
from .models import Profile
from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'age',
            'weight', 
            'height',
            'weight_unit_preference',
            'height_unit_preference',
            'distance_unit_preference',
        ]
        widgets = {
            'weight_unit_preference': forms.HiddenInput(),
            'height_unit_preference': forms.HiddenInput(),
            'distance_unit_preference': forms.HiddenInput(),
        }
