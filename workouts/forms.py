from django import forms
from .models import Workout, WorkoutRoute


class WorkoutForm(forms.ModelForm):
    """
    Form for manual workout logging.
    Allows users to input workout details without wearable devices.
    """
    class Meta:
        model = Workout
        fields = ['title', 'workout_type', 'description', 'duration', 
                  'calories', 'distance', 'workout_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Morning Run in Central Park'
            }),
            'workout_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes about your workout (optional)'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in minutes',
                'min': 1
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calories burned (optional)',
                'min': 0
            }),
            'distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distance in km (optional)',
                'step': '0.01',
                'min': 0
            }),
            'workout_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value for workout_date field
        if self.instance and self.instance.pk:
            self.initial['workout_date'] = self.instance.workout_date.strftime('%Y-%m-%dT%H:%M')


class WorkoutRouteForm(forms.ModelForm):
    """
    Form for recording workout routes.
    The route_data will be populated via JavaScript map interface.
    """
    class Meta:
        model = WorkoutRoute
        fields = ['route_data', 'start_location', 'end_location']
        widgets = {
            'route_data': forms.HiddenInput(),
            'start_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Starting point (optional)'
            }),
            'end_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ending point (optional)'
            }),
        }

