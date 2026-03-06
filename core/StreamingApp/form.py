from django import forms
from django.forms import ModelForm
from .models import Genre, Producer, Studio, Series, Episode

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
        fields = '__all__'

class AddGenreForm(ModelForm):
    class Meta:
        # Meta attribute must be lowercase 'model'
        model = Genre
        fields = '__all__'

class AddEpisodeForm(ModelForm):
    class Meta:
        model = Episode
        fields = ['episode_number', 'episode_title', 'video_id']

class ViewerRegisterForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
