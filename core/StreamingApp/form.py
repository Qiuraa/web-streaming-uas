from django import forms
from django.forms import ModelForm
from .models import Producer, Studio, Series, Episode

class AddProducerForm(ModelForm):
    class Meta:
        model = Producer
        fields = ['name']

class AddStudioForm(ModelForm):
    class Meta:
        model = Studio
        fields = ['studio_name']

class AddSeriesForm(ModelForm):
    class Meta:
        model = Series
        fields = [
            'title', 'alternate_title', 'sypnosis',
            'total_episodes', 'season_number', 'status',
            'aired_start_date', 'aired_end_date', 'premiered_season',
            'premiered_year', 'producer', 'studio',
            'duration_minutes', 'rating'
        ]