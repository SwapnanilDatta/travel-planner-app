from django import forms
from .models import Trip, UserPreference
import json

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['destination_city', 'start_date', 'end_date', 'hotel_name']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['budget', 'trip_style', 'age_group', 'mobility_constraints']
        widgets = {
            'trip_style': forms.Select(choices=[
                ('Relaxed', 'Relaxed'),
                ('Moderate', 'Moderate'),
                ('Fast-paced', 'Fast-paced'),
            ], attrs={'class': 'form-select'}),
            'age_group': forms.Select(choices=[
                ('18-25', '18-25'),
                ('26-35', '26-35'),
                ('36-50', '36-50'),
                ('50+', '50+'),
            ], attrs={'class': 'form-select'}),
            'mobility_constraints': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
