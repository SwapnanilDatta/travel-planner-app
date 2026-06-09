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
    interests_str = forms.CharField(
        label='Interests (comma separated)',
        help_text='e.g., History, Architecture, Food, Nature',
        required=False
    )

    class Meta:
        model = UserPreference
        fields = ['budget', 'trip_style', 'walking_limit', 'days']

    def save(self, commit=True):
        instance = super().save(commit=False)
        interests_str = self.cleaned_data.get('interests_str', '')
        if interests_str:
            interests_list = [i.strip() for i in interests_str.split(',') if i.strip()]
            instance.interests = interests_list
        else:
            instance.interests = []
            
        if commit:
            instance.save()
        return instance
