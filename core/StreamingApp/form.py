from django import forms
from django.forms import ModelForm
from .models import Genre, Producer, Studio, Series, Episode
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

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


class EmailAuthenticationForm(AuthenticationForm):
    """Authentication form that accepts an email in the 'username' field.

    We keep the field name 'username' because Django's LoginView and
    AuthenticationForm internals expect it. However the input is validated
    as an email and resolved to the actual user.username before calling
    authenticate()."""
    # Replace the default username field with an EmailField (keeps the name)
    username = forms.EmailField(label=_("Email"), widget=forms.EmailInput(attrs={'autofocus': True}))

    def clean(self):
        # The incoming 'username' field contains the user's email.
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid_login'], code='invalid_login')

        # Resolve to internal username and authenticate
        self.user_cache = authenticate(self.request, username=user.username, password=password)
        if self.user_cache is None:
            raise forms.ValidationError(self.error_messages['invalid_login'], code='invalid_login')

        self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class ViewerProfileForm(ModelForm):
    class Meta:
        model = get_user_model()
        # Allow editing email and profile picture instead of username
        fields = ['email', 'profile_picture_url']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
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