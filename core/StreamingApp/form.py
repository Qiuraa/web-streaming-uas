from django import forms
from django.forms import ModelForm
from .models import Genre, Producer, Studio, Series, Episode
from django.contrib.auth import get_user_model

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


class ViewerProfileForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'profile_picture_url']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

from django.core.exceptions import ValidationError
from .models import SpotLightSeries


class AddSpotlightSeriesForm(forms.Form):
    # A free-text search input plus a hidden series_id field filled by JS.
    series_search = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search series...'}))
    series_id = forms.UUIDField(required=True, widget=forms.HiddenInput())
    image = forms.ImageField(required=False)

    def clean_series_id(self):
        sid = self.cleaned_data.get('series_id')
        try:
            series = Series.objects.get(series_id=sid)
        except Series.DoesNotExist:
            raise ValidationError('Selected series does not exist')
        # ensure only published series can be spotlighted
        if not series.is_published:
            raise ValidationError('Selected series is not published')
        return sid

    def save(self):
        sid = self.cleaned_data.get('series_id')
        series = Series.objects.get(series_id=sid)
        # create spotlight entry if not exists
        spotlight, created = SpotLightSeries.objects.get_or_create(series=series)
        # if an image was provided, attach it and save
        img = self.cleaned_data.get('image')
        if img:
            spotlight.image = img
            spotlight.save()
        return spotlight