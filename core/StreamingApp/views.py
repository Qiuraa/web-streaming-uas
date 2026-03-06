from urllib import response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse
from django.contrib.auth import logout, get_user_model

from core.StreamingApp import form
from core.StreamingApp.form import AddGenreForm, AddProducerForm, AddStudioForm, AddSeriesForm, AddEpisodeForm
from .models import Genre, Producer, Series, Studio, Episode



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
            username = viewer_register_form.cleaned_data['username']
            email = viewer_register_form.cleaned_data['email']
            password = viewer_register_form.cleaned_data['password']
            user = get_user_model().objects.create_user(username=username, email=email, password=password)
            user.role = 'viewer'
            user.save()
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


class AdminHomepageView(AdminRequiredView):
    def get(self,request):
        return render(request, 'admin/admin_homepage.html')
    
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
        edit_film_form = AddSeriesForm(request.POST, instance=series)
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
        series = Series.objects.all()
        return render(request, 'guest/home_page.html', {
            'series': series,
        })

class SearchResultsView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        search_results = Series.objects.filter(title__icontains=query).order_by('title')
        return render(request, 'guest/search_results.html', {
            'search_results': search_results,
            'query': query,
        })

class DetailFilmGuestView(View):
    def get(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        # Prefer to show episode number 1 on the detail page. If episode 1 doesn't exist,
        # fall back to the first episode ordered by episode_number.
        episode = Episode.objects.filter(series=series, episode_number=1).first()
        if not episode:
            episode = Episode.objects.filter(series=series).order_by('episode_number').first()
        # compute origin to include in the YouTube embed query string — helps avoid some embed configuration errors
        origin = f"{request.scheme}://{request.get_host()}"
        return render(request, 'guest/detail_film_guest.html', {
            'series': series,
            'episode': episode,
            'origin': origin,
        })

class ViewerHomepageView(View):
    def get(self, request, user_id):
        series = Series.objects.all()
        return render(request, 'viewer/viewer_homepage.html', {
            'series': series,
        })

# Provide a proper LoginView for the admin login page so unauthenticated
# users can reach the login form. Keep the viewer login as a special LoginView.
admin_login = LoginView.as_view(
    template_name='admin/admin_login.html',
    redirect_authenticated_user=True,
)
viewer_login = ViewerRequiredView.as_view()
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
detail_film_guest = DetailFilmGuestView.as_view()
viewer_homepage = ViewerHomepageView.as_view()
viewer_register = ViewerRegisterView.as_view()