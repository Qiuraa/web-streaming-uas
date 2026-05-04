from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse
from django.contrib.auth import logout, get_user_model
from django.db import IntegrityError

from core.StreamingApp import form
from core.StreamingApp.form import AddGenreForm, AddProducerForm, AddStudioForm, AddSeriesForm, AddEpisodeForm
from .models import Genre, Producer, Series, SpotLightSeries, Studio, Episode, WatchHistory, Watchlist, Comment
import json
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.core.serializers.json import DjangoJSONEncoder


class ViewerRequiredView(LoginView):
    template_name = "guest/viewer_login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)  # log out any authenticated user to ensure a clean session for the viewer role
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)

        # jika bukan viewer → logout dan kembali ke login
        if self.request.user.role != "viewer":
            logout(self.request)
            return redirect("viewer_login")

        return response

    def get_success_url(self):
        return reverse("viewer_homepage", kwargs={'user_id': self.request.user.user_id})

class ViewerRegisterView(View):
    def get(self, request):
        viewer_register_form = form.ViewerRegisterForm()
        return render(request, 'guest/viewer_register.html', {
            'viewer_register_form': viewer_register_form,
        })
    
    def post(self, request):
        viewer_register_form = form.ViewerRegisterForm(request.POST)
        if viewer_register_form.is_valid():
            # Create a new user with the provided username, email, and password
            from django.contrib.auth.models import User
            # Use provided username if present, otherwise derive one from the email
            username = viewer_register_form.cleaned_data.get('username')
            email = viewer_register_form.cleaned_data['email']
            password = viewer_register_form.cleaned_data['password']
            UserModel = get_user_model()
            if not username:
                # derive base username from email local part
                base = email.split('@')[0]
                candidate = base
                suffix = 1
                # ensure uniqueness of username
                while UserModel.objects.filter(username=candidate).exists():
                    candidate = f"{base}{suffix}"
                    suffix += 1
                username = candidate

            # pre-check: if the email is already registered, add form error
            if UserModel.objects.filter(email__iexact=email).exists():
                viewer_register_form.add_error('email', 'This email is already registered. Please use a different email or login to your existing account.')
                return render(request, 'guest/viewer_register.html', {
                    'viewer_register_form': viewer_register_form,
                })

            # pre-check: if user supplied a username that already exists, add form error
            if viewer_register_form.cleaned_data.get('username') and UserModel.objects.filter(username__iexact=username).exists():
                viewer_register_form.add_error('username', 'This username is already taken. Please choose another.')
                return render(request, 'guest/viewer_register.html', {
                    'viewer_register_form': viewer_register_form,
                })

            try:
                user = UserModel.objects.create_user(username=username, email=email, password=password)
                user.role = 'viewer'
                user.save()
            except IntegrityError:
                # Handle rare race condition where username was created after the check
                viewer_register_form.add_error('username', 'This username is already taken. Please choose another.')
                return render(request, 'guest/viewer_register.html', {
                    'viewer_register_form': viewer_register_form,
                })
            return redirect('viewer_login')
        return render(request, 'guest/viewer_register.html', {
            'viewer_register_form': viewer_register_form,
        })

class AdminRequiredView(LoginRequiredMixin, View):
    # For admin-only pages. Unauthenticated users are redirected to the
    # named admin login view so the `next` parameter is preserved.
    login_url = 'admin_login'
    allowed_roles = ["admin"]

    def dispatch(self, request, *args, **kwargs):
        # If the user isn't authenticated, LoginRequiredMixin will redirect
        # to `login_url` automatically when we call super().dispatch; we
        # still make an explicit check so we can add role-based behavior.
        if not request.user.is_authenticated:
            return redirect(f"{reverse('admin_login')}?next={request.path}")

        # If authenticated but not an admin, send them to the public homepage.
        if getattr(request.user, 'role', None) != 'admin':
            return redirect('homepage')

        return super().dispatch(request, *args, **kwargs)


class AdminHomepageView(AdminRequiredView, View):
    def get(self,request):
        return render(request, 'admin/admin_homepage.html')
    
    def post(self, request):
            logout(request)
            return redirect('homepage')
    
class AddProducerView(AdminRequiredView):
    def get(self, request):
        # Provide an empty form instance so template can render it
        add_producer_form = AddProducerForm()
        return render(request, 'admin/add_producer.html', {
            'add_producer_form': add_producer_form,
        })

    def post(self, request):
        add_producer_form = AddProducerForm(request.POST)
        if add_producer_form.is_valid():
            add_producer_form.save()
            return redirect('manage_producer')
        # Re-render with bound form to show validation errors
        return render(request, 'admin/add_producer.html', {
            'add_producer_form': add_producer_form,
        })


class AddStudioView(AdminRequiredView):
    def get(self, request):
        add_studio_form = AddStudioForm()
        return render(request, 'admin/add_studio.html', {
            'add_studio_form': add_studio_form
        })
    
    def post(self,request):
        add_studio_form = AddStudioForm(request.POST)
        if add_studio_form.is_valid():
            add_studio_form.save()
            return redirect('manage_studio')
        return render(request, 'admin/add_studio.html', {
            'add_studio_form' : add_studio_form
        })

class ManageProducerView(AdminRequiredView):
    def get(self,request):
        producers = Producer.objects.all()
        return render(request, 'admin/manage_producer.html', {
            'producers': producers,
        })

class ManageStudioView(AdminRequiredView):
    def get(self,request):
        studios = Studio.objects.all()
        return render(request, 'admin/manage_studio.html', {
            'studios' : studios
        })

class EditProducerView(AdminRequiredView):
    def get(self,request, producer_id):
        producer = get_object_or_404(Producer, producer_id=producer_id)
        edit_producer_form = AddProducerForm(instance=producer)
        return render(request, 'admin/edit_producer.html', {
            'edit_producer_form': edit_producer_form,
        })
    
    def post(self,request, producer_id):
        producer = get_object_or_404(Producer, producer_id= producer_id)
        edit_producer_form = AddProducerForm(request.POST, instance= producer)
        if edit_producer_form.is_valid():
            edit_producer_form.save()
            return redirect('manage_producer')
        return render(request, 'admin/edit_producer.html',{
            'edit_producer_form' : edit_producer_form
        })

class DeleteProducerView(AdminRequiredView):
    def post(self, request, producer_id):
        # request must be accepted as first argument for POST handlers
        producer = get_object_or_404(Producer, producer_id=producer_id)
        producer.delete()
        return redirect('manage_producer')

class EditStudioView(AdminRequiredView):
    def get(self,request, studio_id):
        studio = get_object_or_404(Studio, studio_id=studio_id)
        edit_studio_form = AddStudioForm(instance=studio)
        return render(request, 'admin/edit_studio.html', {
            'edit_studio_form': edit_studio_form,
        })
    
    def post(self, request, studio_id):
        studio= get_object_or_404(Studio, studio_id=studio_id)
        edit_studio_form = AddStudioForm(request.POST, instance=studio)
        if edit_studio_form.is_valid():
            edit_studio_form.save()
            return redirect('manage_studio')
        return render(request, 'admin/edit_studio.html', {
            'edit_studio_form': edit_studio_form,
        })

class DeleteStudioView(AdminRequiredView):
    def post(self, request, studio_id):
        # include request parameter so Django dispatch works correctly
        studio = get_object_or_404(Studio, studio_id=studio_id)
        studio.delete()
        return redirect('manage_studio')

# NOTE: ManageFilmView is defined further below with full context (series list).
# The earlier empty placeholder ManageFilmView was removed to avoid a duplicate class
# which could shadow the real implementation.

class AddFilmView(AdminRequiredView):
    def get(self, request):
        add_film_form = AddSeriesForm()
        return render(request, 'admin/add_film.html', {
            'add_film_form': add_film_form
        })
    
    def post(self,request):
        # include request.FILES so uploaded files (thumbnail_picture) are processed
        add_film_form = AddSeriesForm(request.POST, request.FILES)
        if add_film_form.is_valid():
            add_film_form.save()
            return redirect('manage_film')
        return render(request, 'admin/add_film.html', {
            'add_film_form': add_film_form
        })
    
class AddGenreView(AdminRequiredView):
    def get(self, request):
        add_genre_form = AddGenreForm()
        return render(request, 'admin/add_genre.html', {
            'add_genre_form': add_genre_form
        })
    
    def post(self, request):
        add_genre_form = AddGenreForm(request.POST)
        if add_genre_form.is_valid():
            add_genre_form.save()
            return redirect('manage_genre')
        return render(request, 'admin/add_genre.html', {
            'add_genre_form': add_genre_form
        })
    
class ManageGenreView(AdminRequiredView):
    def get(self, request):
        genres = Genre.objects.all().order_by('name')
        return render(request, 'admin/manage_genre.html', {
            'genres': genres
        })

class EditGenreView(AdminRequiredView):
    def get(self, request, genre_id):
        genre = get_object_or_404(Genre, genre_id=genre_id)
        edit_genre_form = AddGenreForm(instance=genre)
        return render(request, 'admin/edit_genre.html', {
            'edit_genre_form': edit_genre_form,
        })
    
    def post(self, request, genre_id):
        genre = get_object_or_404(Genre, genre_id=genre_id)
        edit_genre_form = AddGenreForm(request.POST, instance=genre)
        if edit_genre_form.is_valid():
            edit_genre_form.save()
            return redirect('manage_genre')
        return render(request, 'admin/edit_genre.html', {
            'edit_genre_form': edit_genre_form,
        })
    
class DeleteGenreView(AdminRequiredView):
    def post(self, request, genre_id):
        genre = get_object_or_404(Genre, genre_id=genre_id)
        genre.delete()
        return redirect('manage_genre')

class ManageFilmView(AdminRequiredView):
    def get(self,request):
        # Provide the list of series only. Do not pass a QuerySet into an exact
        # lookup for Episode (that caused ValueError previously). The detail
        # page selects the default episode itself.
        series = Series.objects.all().order_by('title')
        return render(request, 'admin/manage_film.html', {
            'series': series,
        })
    
class EditFilmView(AdminRequiredView):
    def get(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        edit_film_form = AddSeriesForm(instance=series)
        return render(request, 'admin/edit_film.html', {
            'edit_film_form' : edit_film_form
        })
    
    def post(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        edit_film_form = AddSeriesForm(request.POST, request.FILES, instance=series)
        if edit_film_form.is_valid():
            edit_film_form.save()
            return redirect('manage_film')
        return render(request, 'admin/edit_film.html', {
            'edit_film_form' : edit_film_form
            })

class DeleteFilmView(AdminRequiredView):
    def post(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        series.delete()
        return redirect('manage_film')
    
class DetailFilmView(AdminRequiredView):
    def get(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        # Prefer to show episode number 1 on the detail page. If episode 1 doesn't exist,
        # fall back to the first episode ordered by episode_number.
        episode = Episode.objects.filter(series=series, episode_number=1).first()
        if not episode:
            episode = Episode.objects.filter(series=series).order_by('episode_number').first()
        # compute origin to include in the YouTube embed query string — helps avoid some embed configuration errors
        origin = f"{request.scheme}://{request.get_host()}"
        return render(request, 'admin/detail_film.html', {
            'series': series,
            'episode': episode,
            'origin': origin,
        })

class ManageEpisodeView(AdminRequiredView):
    def get(self, request, series_id):
        # Show episodes for a specific series
        series = get_object_or_404(Series, series_id=series_id)
        episodes = Episode.objects.filter(series=series).order_by('episode_number')
        return render(request, 'admin/manage_episode.html', {
            'series': series,
            'episodes': episodes,
        })
    
class AddEpisodeView(AdminRequiredView):
    def get(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        # create empty form for adding a new Episode for this Series
        add_episode_form = AddEpisodeForm()
        return render(request, 'admin/add_episode.html', {
            'add_episode_form': add_episode_form,
            'series': series,
        })

    def post(self,request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        add_episode_form = AddEpisodeForm(request.POST)
        if add_episode_form.is_valid():
            # assign the FK to the parent Series before saving
            episode = add_episode_form.save(commit=False)
            episode.series = series
            episode.save()
            return redirect('manage_episode', series_id=series.series_id)
        return render(request, 'admin/add_episode.html', {
            'add_episode_form': add_episode_form,
            'series': series,
        })

class EditEpisodeView(AdminRequiredView):
    def get(self, request, episode_id):
        episode = get_object_or_404(Episode, episode_id=episode_id)
        edit_episode_form = AddEpisodeForm(instance=episode)
        # include series in context in case template needs it or for redirect target
        return render(request, 'admin/edit_episode.html', {
            'edit_episode_form': edit_episode_form,
            'series': episode.series,
            'episode': episode,
        })
    
    def post(self, request, episode_id):
        episode = get_object_or_404(Episode, episode_id=episode_id)
        edit_episode_form = AddEpisodeForm(request.POST, instance=episode)
        if edit_episode_form.is_valid():
            edit_episode_form.save()
            # redirect back to the episode list for the parent series
            return redirect('manage_episode', series_id=episode.series.series_id)
        return render(request, 'admin/edit_episode.html', {
            'edit_episode_form':edit_episode_form,
            'series': episode.series,
            'episode': episode,
        })

class DeleteEpisodeView(AdminRequiredView):
    def post(self, request, episode_id):
        episode = get_object_or_404(Episode, episode_id=episode_id)
        series_id = episode.series.series_id
        episode.delete()
        # Redirect back to the episode list for the parent series
        return redirect('manage_episode', series_id=series_id)


class PlayEpisodeView(AdminRequiredView):
    def get(self, request, episode_id):
        episode = get_object_or_404(Episode, episode_id=episode_id)
        series = episode.series
        # compute origin to include in the YouTube embed query string — helps avoid some embed configuration errors
        origin = f"{request.scheme}://{request.get_host()}"
        return render(request, 'admin/play_episode.html', {
            'episode': episode,
            'origin': origin,
        })

class HomepageView(View):
    def get(self, request):
        featured_series = Series.objects.filter(is_published=True).annotate(
            total_views=Coalesce(Sum('episode__view_count'), Value(0))
            ).order_by('-total_views')[:10]
        # `series` in the template is used for the Featured section; provide featured_series there
        series = featured_series
        # Show the most recently published series in the "New Anime" section.
        new_series = Series.objects.filter(
            is_published=True,
            is_published_date__isnull=False
        ).prefetch_related('genre').order_by('-is_published_date')[:10]

        # Also supply upcoming (not yet published) series for the "Upcoming Releases" section.
        upcoming_series = Series.objects.filter(is_published=False).order_by('created_at')[:10]

        spotlight_series = SpotLightSeries.objects.filter(series__is_published=True).select_related('series').order_by('-created_at')[:5]
        
        # Get continue watching: only the latest watched episode per series
        continue_watching = []
        if request.user.is_authenticated:
            # Get latest watched episode per series
            watch_history_by_series = {}
            watch_history_list = WatchHistory.objects.filter(user=request.user).select_related('episode__series', 'episode').order_by('-last_watched_at')
            for wh in watch_history_list:
                series_id = wh.episode.series.series_id
                if series_id not in watch_history_by_series:
                    watch_history_by_series[series_id] = wh
            continue_watching = list(watch_history_by_series.values())[:5]

            # Compute progress_percent for each history item so the template progress bar works
            for wh in continue_watching:
                duration_sec = (wh.episode.series.duration_minutes or 1) * 60
                wh.progress_percent = min(int((wh.progress_seconds / duration_sec) * 100), 100) if duration_sec > 0 else 0

        return render(request, 'guest/home_page.html', {
            'featured_series': featured_series,
            'series': series,
            'new_series': new_series,
            'upcoming_series': upcoming_series,
            'spotlight_series': spotlight_series,
            'continue_watching': continue_watching,
        })

class SearchResultsView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        search_results = Series.objects.filter(title__icontains=query).order_by('title')
        return render(request, 'guest/search_results.html', {
            'search_results': search_results,
            'query': query,
        })

class WatchFilmGuestView(View):
    def get(self, request, series_id, episode_id):
        series = get_object_or_404(Series, series_id=series_id)

        episode = get_object_or_404(
            Episode,
            episode_id=episode_id,
            series=series
        )
        origin = f"{request.scheme}://{request.get_host()}"
        user = request.user if request.user.is_authenticated else None

        comments = Comment.objects.filter(
        episode=episode,
        is_deleted=False
        ).select_related('user').order_by('-created_at')

        return render(request, 'guest/watch_film_guest.html', {
            'series': series,
            'episode': episode,
            'origin': origin,
            'comments': comments,
            'user': user,
        })
    
class DetailFilmGuestView(View):
    def get(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        
        # Find the last watched episode for this series (if user is authenticated)
        last_watched_episode = None
        if request.user.is_authenticated:
            last_watch = WatchHistory.objects.filter(
                user=request.user,
                episode__series=series
            ).select_related('episode').order_by('-last_watched_at').first()
            if last_watch:
                last_watched_episode = last_watch.episode
        
        return render(request, 'guest/detail_film_guest.html', {
            'series': series,
            'last_watched_episode': last_watched_episode,
        })

class ViewerHomepageView(View):
    def get(self, request, user_id):
        # Determine featured series by total episode views (top by sum of episode.view_count)
        featured_series = Series.objects.filter(is_published=True).annotate(
            total_views=Coalesce(Sum('episode__view_count'), Value(0))
        ).order_by('-total_views')[:10]
        # `series` in the template is used for the Featured section; provide featured_series there
        series = featured_series

        # Get continue watching: only the latest watched episode per series
        all_history = WatchHistory.objects.filter(
            user__user_id=user_id
        ).select_related('episode__series', 'episode').order_by('-last_watched_at')

        watch_history_by_series = {}
        for wh in all_history:
            sid = wh.episode.series.series_id
            if sid not in watch_history_by_series:
                watch_history_by_series[sid] = wh
        watch_history_list = list(watch_history_by_series.values())[:5]

        # Compute progress_percent for each history item so the template progress bar works
        for wh in watch_history_list:
            duration_sec = (wh.episode.series.duration_minutes or 1) * 60
            wh.progress_percent = min(int((wh.progress_seconds / duration_sec) * 100), 100) if duration_sec > 0 else 0

        # Show the most recently published series in the "New Anime" section.
        new_series = Series.objects.filter(
            is_published=True,
            is_published_date__isnull=False
        ).prefetch_related('genre').order_by('-is_published_date')[:10]

        # Also supply upcoming (not yet published) series for the "Upcoming Releases" section.
        upcoming_series = Series.objects.filter(is_published=False).order_by('created_at')[:10]

        spotlight_series = SpotLightSeries.objects.filter(series__is_published=True).select_related('series').order_by('-created_at')[:5]

        return render(request, 'viewer/viewer_homepage.html', {
            'series': series,
            'watch_history_list': watch_history_list,
            'new_series': new_series,
            'upcoming_series': upcoming_series,
            'spotlight_series': spotlight_series,
        })

class BaseUserView(View):
    def get(self, request):
        user = get_user_model().objects.filter(user_id=request.user.user_id).first()
        return render(request, 'base_user/base_user.html', {
            'user': user,
        })
    
class ViewerProfileView(LoginRequiredMixin, View):
    # Use LoginRequiredMixin so we don't run the ViewerRequiredView.dispatch which
    # intentionally logs out an authenticated user (that behavior is only for the
    # dedicated viewer login page). Ensure only viewers (or admins) can view profiles.
    login_url = 'viewer_login'

    def get(self, request, user_id):
        # Require authenticated user (LoginRequiredMixin already enforces this
        # but we keep an explicit guard for clarity).
        if not request.user.is_authenticated:
            return redirect(f"{reverse('viewer_login')}?next={request.path}")

        # Only allow the profile owner or admins to view this page.
        if getattr(request.user, 'role', None) != 'admin' and str(request.user.user_id) != str(user_id):
            return redirect('homepage')

        # Fetch the requested user by UUID (user_id param). If missing, redirect.
        user = get_user_model().objects.filter(user_id=user_id).first()
        if not user:
            return redirect('homepage')

        return render(request, 'viewer/viewer_profile.html', {
            'user': user,
        })

    def post(self, request, user_id):
        user_id = get_user_model().objects.filter(user_id=user_id).first()
        if user_id:
            logout(request)
            return redirect('homepage')

class UpdateProfileView(LoginRequiredMixin, View):
    login_url = 'viewer_login'

    def get(self, request, user_id):
        # ensure users can only edit their own profile (or admins)
        if not request.user.is_authenticated:
            return redirect(f"{reverse('viewer_login')}?next={request.path}")
        if str(request.user.user_id) != str(user_id) and getattr(request.user, 'role', None) != 'admin':
            return redirect('homepage')
        from core.StreamingApp.form import ViewerProfileForm
        form = ViewerProfileForm(instance=request.user)
        return render(request, 'viewer/viewer_profile.html', {
            'user': request.user,
            'form': form,
        })

    def post(self, request, user_id):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('viewer_login')}?next={request.path}")
        if str(request.user.user_id) != str(user_id) and getattr(request.user, 'role', None) != 'admin':
            return redirect('homepage')
        from core.StreamingApp.form import ViewerProfileForm
        form = ViewerProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('viewer_profile', user_id=request.user.user_id)
        return render(request, 'viewer/viewer_profile.html', {
            'user': request.user,
            'form': form,
        })
    
class WatchHistoryView(View):

    def get(self, request, user_id=None):
        # only allow authenticated viewers to see watch history
        if not request.user.is_authenticated:
            return redirect(f"{reverse('viewer_login')}?next={request.path}")
        if getattr(request.user, 'role', None) != 'viewer':
            return redirect('homepage')

        # If no user_id provided, show the current user's watch history.
        if user_id is None:
            user = request.user
            all_history = WatchHistory.objects.filter(user=user).select_related('episode__series').order_by('-last_watched_at')
        else:
            # allow admins to view other users' history by UUID
            all_history = WatchHistory.objects.filter(user__user_id=user_id).select_related('episode__series').order_by('-last_watched_at')

        # Deduplicate: only keep the most recently watched episode per series
        seen_series = {}
        for wh in all_history:
            sid = wh.episode.series.series_id
            if sid not in seen_series:
                seen_series[sid] = wh
        watch_history_list = list(seen_series.values())

        # Compute progress_percent for each history item so the template progress bar works
        for wh in watch_history_list:
            duration_sec = (wh.episode.series.duration_minutes or 1) * 60
            wh.progress_percent = min(int((wh.progress_seconds / duration_sec) * 100), 100) if duration_sec > 0 else 0

        return render(request, 'viewer/viewer_watch_history.html', {
            'watch_history_list': watch_history_list,
        })

    def post(self, request):
        # This POST handler can be used to update watch history progress from the frontend.
        # Protect against anonymous users.
        if not request.user.is_authenticated:
            return redirect('viewer_login')
        if getattr(request.user, 'role', None) != 'viewer':
            return redirect('homepage')

        episode_id = request.POST.get('episode_id')
        progress_seconds = request.POST.get('progress_seconds')
        if episode_id and progress_seconds is not None:
            try:
                episode = Episode.objects.get(episode_id=episode_id)
                watch_history, created = WatchHistory.objects.get_or_create(user=request.user, episode=episode)
                watch_history.progress_seconds = progress_seconds
                watch_history.save()
                return redirect('viewer_homepage', user_id=request.user.user_id)
            except Episode.DoesNotExist:
                pass  # handle invalid episode_id if necessary
        return redirect('viewer_homepage', user_id=request.user.user_id)



def save_progress(request):

    if request.method == "POST":
        # ensure user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"status": "forbidden"}, status=403)

        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"status": "bad_request"}, status=400)

        episode_id = data.get("episode_id")
        progress = data.get("progress_seconds")

        if episode_id is None or progress is None:
            return JsonResponse({"status": "bad_request"}, status=400)

        # find the Episode instance (episode_id is UUID string)
        try:
            episode = Episode.objects.get(episode_id=episode_id)
        except Episode.DoesNotExist:
            return JsonResponse({"status": "not_found"}, status=404)

        # parse progress into int safely
        try:
            progress_int = int(progress)
        except Exception:
            progress_int = 0

        watch, created = WatchHistory.objects.get_or_create(
            user=request.user,
            episode=episode,
            defaults={'progress_seconds': progress_int}
        )

        # If this is the first time this user has a WatchHistory for this episode
        # and they have progressed beyond 0 seconds, count it as a view for the episode.
        if created and progress_int > 0:
            try:
                episode.view_count = (episode.view_count or 0) + 1
                episode.save(update_fields=['view_count', 'updated_at'])
            except Exception:
                # ignore failures to avoid breaking progress saving
                pass

        # update only if progressed further
        if not created and progress_int > watch.progress_seconds:
            watch.progress_seconds = progress_int
            watch.save()

        return JsonResponse({"status": "ok"})

class NewReleasesView(View):
    def get(self, request):

        new_series = Series.objects.filter(
            is_published=True,
            is_published_date__isnull=False
        ).prefetch_related('genre').order_by('-is_published_date')[:10]

        return render(request, "viewer/viewer_homepage.html", {
            "new_series": new_series
        })

class UpcomingReleasesView(View):
    def get(self, request):
        upcoming_series = Series.objects.filter(is_published=False).order_by('created_at')[:5]
        return render(request, "viewer/viewer_homepage.html", {
            "upcoming_series": upcoming_series
        })
    
class FeaturedSeriesView(View):
    def get(self, request):
        featured_series = Series.objects.filter(is_published=True).annotate(
            total_views=Coalesce(Sum('episode__view_count'), Value(0))
        ).order_by('-total_views')[:6]
        return render(request, "viewer/viewer_homepage.html", {
            "featured_series": featured_series
        })

class ManageSpotlightSeriesView(AdminRequiredView):
    def get(self, request):
        spotlight_series = SpotLightSeries.objects.select_related('series').order_by('-created_at')
        return render(request, 'admin/manage_spotlight_series.html', {
            'spotlight_series': spotlight_series
        })
    
    # Keep this view for listing/manage actions; deletion is handled by a small
    # function-based endpoint below which matches the URL kwarg name used in urls.py.
    def post(self, request, spotlight_id=None):
        # Optional: support form-based deletions targeting this view
        if spotlight_id:
            spotlight = get_object_or_404(SpotLightSeries, spotlight_id=spotlight_id)
            spotlight.delete()
        return redirect('manage_spotlight_series')


def delete_spotlight_series(request, spotlight_series_id):
    """Delete a SpotLightSeries by its UUID (used by the admin delete URL).

    The URL pattern uses the name 'spotlight_series_id' so this function
    accepts that kwarg name to avoid Django passing an unexpected param name.
    """
    # Only allow admin users — reuse the same check as AdminRequiredView
    if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'admin':
        return redirect('admin_login')

    spotlight = get_object_or_404(SpotLightSeries, spotlight_series_id=spotlight_series_id)
    spotlight.delete()
    return redirect('manage_spotlight_series')


def episode_comments_json(request, series_id, episode_id):
    """Return JSON list of comments for a given episode.

    This endpoint is used by the client-side episode switcher to refresh
    comments without a full page reload.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'method_not_allowed'}, status=405)

    series = get_object_or_404(Series, series_id=series_id)
    episode = get_object_or_404(Episode, episode_id=episode_id, series=series)

    comments_qs = Comment.objects.filter(episode=episode, is_deleted=False).select_related('user').order_by('-created_at')
    comments = [
        {
            'comment_id': str(c.comment_id),
            'user': c.user.username,
            'content': c.content,
            'created_at': c.created_at.isoformat(),
        }
        for c in comments_qs
    ]

    return JsonResponse({'comments': comments})

class AddSpotlightSeriesView(View):
    def get(self, request):
        add_spotlight_form = form.AddSpotlightSeriesForm()
        # provide published series metadata for client-side search suggestions
        published_series = list(Series.objects.filter(is_published=True).values('series_id', 'title'))
        published_series_json = json.dumps(published_series, cls=DjangoJSONEncoder)
        return render(request, 'admin/add_spotlight_series.html', {
            'add_spotlight_form': add_spotlight_form,
            'published_series_json': published_series_json,
        })
    
    def post(self, request):
        add_spotlight_form = form.AddSpotlightSeriesForm(request.POST, request.FILES)
        if add_spotlight_form.is_valid():
            add_spotlight_form.save()
            return redirect('manage_spotlight_series')
        return render(request, 'admin/add_spotlight_series.html', {
            'add_spotlight_form': add_spotlight_form
        })

class ViewerAddWatchlistView(LoginRequiredMixin, View):
    login_url = 'viewer_login'

    def post(self, request, series_id):
        # Only allow authenticated viewers to add to watchlist
        if not request.user.is_authenticated:
            return redirect('viewer_login')
        if getattr(request.user, 'role', None) != 'viewer':
            return redirect('homepage')

        series = get_object_or_404(Series, series_id=series_id)
        
        Watchlist.objects.get_or_create(user=request.user, series=series)
        return redirect('detail_film_guest', series_id=series_id)

class ViewerWatchlistView(LoginRequiredMixin, View):
    login_url = 'viewer_login'

    def get(self, request):
        watchlist = Watchlist.objects.filter(user=request.user).select_related('series').order_by('-created_at')
        return render(request, 'viewer/viewer_watchlist.html', {
            'watchlist': watchlist
        })

class ViewerRemoveWatchlistView(LoginRequiredMixin, View):
    login_url = 'viewer_login'

    def post(self, request, series_id):
        if not request.user.is_authenticated:
            return redirect('viewer_login')
        if getattr(request.user, 'role', None) != 'viewer':
            return redirect('homepage')

        series = get_object_or_404(Series, series_id=series_id)
        Watchlist.objects.filter(user=request.user, series=series).delete()
        return redirect('watchlist')

class ViewerCommentView(LoginRequiredMixin, View):
    login_url = 'viewer_login'

    def get(self, request, series_id, episode_id):
        series = get_object_or_404(Series, series_id=series_id)
        episode = get_object_or_404(Episode, episode_id=episode_id, series=series)
        comments = Comment.objects.filter(episode=episode, is_deleted=False).order_by('-created_at').select_related('user')
        origin = f"{request.scheme}://{request.get_host()}"
        # Pass the episode and origin so the watch page can render the player and comments
        return render(request, 'guest/watch_film_guest.html', {
            'series': series,
            'episode': episode,
            'origin': origin,
            'comments': comments,
            'user': request.user,
        })

    def post(self, request, series_id, episode_id):

        if getattr(request.user, 'role', None) != 'viewer':
            return redirect('homepage')

        series = get_object_or_404(Series, series_id=series_id)
        episode = get_object_or_404(Episode, episode_id=episode_id)
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                user=request.user,
                series=series,
                episode=episode,
                content=content
            )

        return redirect('watch_film_guest', series_id=series_id, episode_id=episode_id)
    
class HomeView(View):
    def get(self, request):
        return render(request, 'guest/home.html')

admin_login = LoginView.as_view(
    template_name='admin/admin_login.html',
    redirect_authenticated_user=True,
    authentication_form=form.EmailAuthenticationForm,
)
viewer_login = ViewerRequiredView.as_view(authentication_form=form.EmailAuthenticationForm)
admin_logout = LogoutView.as_view(next_page='admin_login')
admin_homepage = AdminHomepageView.as_view()
add_producer = AddProducerView.as_view()
add_studio = AddStudioView.as_view()
manage_producer = ManageProducerView.as_view()
manage_studio = ManageStudioView.as_view()
edit_producer = EditProducerView.as_view()
edit_studio = EditStudioView.as_view()
delete_producer = DeleteProducerView.as_view()
delete_studio = DeleteStudioView.as_view()
manage_film = ManageFilmView.as_view()
add_film = AddFilmView.as_view()
add_genre = AddGenreView.as_view()
manage_genre = ManageGenreView.as_view()
edit_genre = EditGenreView.as_view()
delete_genre = DeleteGenreView.as_view()
manage_film = ManageFilmView.as_view()
edit_film = EditFilmView.as_view()
delete_film = DeleteFilmView.as_view()
manage_episode = ManageEpisodeView.as_view()
add_episode = AddEpisodeView.as_view()
detail_film = DetailFilmView.as_view()
edit_episode = EditEpisodeView.as_view()
delete_episode = DeleteEpisodeView.as_view()
play_episode = PlayEpisodeView.as_view()
homepage = HomepageView.as_view()
search_results = SearchResultsView.as_view()
watch_film_guest = WatchFilmGuestView.as_view()
viewer_homepage = ViewerHomepageView.as_view()
viewer_register = ViewerRegisterView.as_view()
viewer_profile = ViewerProfileView.as_view()
update_profile = UpdateProfileView.as_view()
# function view - don't call it when assigning
save_progress = save_progress
watch_history = WatchHistoryView.as_view()
new_releases = NewReleasesView.as_view()
upcoming_releases = UpcomingReleasesView.as_view()
featured_series = FeaturedSeriesView.as_view()
manage_spotlight_series = ManageSpotlightSeriesView.as_view()
add_spotlight_series = AddSpotlightSeriesView.as_view()
add_to_watchlist = ViewerAddWatchlistView.as_view()
view_watchlist = ViewerWatchlistView.as_view()
detail_film_guest = DetailFilmGuestView.as_view()
remove_from_watchlist = ViewerRemoveWatchlistView.as_view()
viewer_comment = ViewerCommentView.as_view()
home = HomeView.as_view()