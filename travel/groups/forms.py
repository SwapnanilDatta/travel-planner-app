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
    VOTE_CHOICES = [(i, str(i)) for i in range(1, 5)]
    
    history_vote = forms.ChoiceField(choices=VOTE_CHOICES, label="History", initial=3, widget=forms.Select(attrs={'class': 'form-select'}))
    food_vote = forms.ChoiceField(choices=VOTE_CHOICES, label="Food", initial=3, widget=forms.Select(attrs={'class': 'form-select'}))
    nature_vote = forms.ChoiceField(choices=VOTE_CHOICES, label="Nature", initial=3, widget=forms.Select(attrs={'class': 'form-select'}))
    shopping_vote = forms.ChoiceField(choices=VOTE_CHOICES, label="Shopping", initial=3, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = UserPreference
        fields = ['budget', 'trip_style', 'walking_limit', 'days']
        widgets = {
            'trip_style': forms.Select(choices=[
                ('Relaxed', 'Relaxed'),
                ('Moderate', 'Moderate'),
                ('Fast-paced', 'Fast-paced'),
            ], attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.category_votes:
            self.fields['history_vote'].initial = self.instance.category_votes.get('History', 3)
            self.fields['food_vote'].initial = self.instance.category_votes.get('Food', 3)
            self.fields['nature_vote'].initial = self.instance.category_votes.get('Nature', 3)
            self.fields['shopping_vote'].initial = self.instance.category_votes.get('Shopping', 3)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.category_votes = {
            'History': int(self.cleaned_data.get('history_vote')),
            'Food': int(self.cleaned_data.get('food_vote')),
            'Nature': int(self.cleaned_data.get('nature_vote')),
            'Shopping': int(self.cleaned_data.get('shopping_vote'))
        }
        if commit:
            instance.save()
        return instance
