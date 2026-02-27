from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View

from core.StreamingApp.form import AddGenreForm, AddProducerForm, AddStudioForm, AddSeriesForm, AddEpisodeForm
from .models import Genre, Producer, Series, Studio, Episode

# @login_required
class AdminHomepageView(View):
    def get(self,request):
        return render(request, 'admin/admin_homepage.html')
    
class AddProducerView(View):
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


class AddStudioView(View):
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

class ManageProducerView(View):
    def get(self,request):
        producers = Producer.objects.all()
        return render(request, 'admin/manage_producer.html', {
            'producers': producers,
        })

class ManageStudioView(View):
    def get(self,request):
        studios = Studio.objects.all()
        return render(request, 'admin/manage_studio.html', {
            'studios' : studios
        })

class EditProducerView(View):
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

class DeleteProducerView(View):
    def post(self, request, producer_id):
        # request must be accepted as first argument for POST handlers
        producer = get_object_or_404(Producer, producer_id=producer_id)
        producer.delete()
        return redirect('manage_producer')

class EditStudioView(View):
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

class DeleteStudioView(View):
    def post(self, request, studio_id):
        # include request parameter so Django dispatch works correctly
        studio = get_object_or_404(Studio, studio_id=studio_id)
        studio.delete()
        return redirect('manage_studio')

class ManageFilmView(View):
    def get(self,request):
        return render(request, 'admin/manage_film.html')

class AddFilmView(View):
    def get(self, request):
        add_film_form = AddSeriesForm()
        return render(request, 'admin/add_film.html', {
            'add_film_form': add_film_form
        })
    
    def post(self,request):
        add_film_form = AddSeriesForm(request.POST)
        if add_film_form.is_valid():
            add_film_form.save()
            return redirect('manage_film')
        return render(request, 'admin/add_film.html', {
            'add_film_form': add_film_form
        })
    
class AddGenreView(View):
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
    
class ManageGenreView(View):
    def get(self, request):
        genres = Genre.objects.all().order_by('name')
        return render(request, 'admin/manage_genre.html', {
            'genres': genres
        })

class EditGenreView(View):
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
    
class DeleteGenreView(View):
    def post(self, request, genre_id):
        genre = get_object_or_404(Genre, genre_id=genre_id)
        genre.delete()
        return redirect('manage_genre')

class ManageFilmView(View):
    def get(self,request):
        series = Series.objects.all().order_by('title')
        return render(request, 'admin/manage_film.html', {
            'series': series
        })
    
class EditFilmView(View):
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

class DeleteFilmView(View):
    def post(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        series.delete()
        return redirect('manage_film')
    
class DetailFilmView(View):
    def get(self, request, series_id):
        series = get_object_or_404(Series, series_id=series_id)
        return render(request, 'admin/detail_film.html', {
            'series': series
        })

class ManageEpisodeView(View):
    def get(self, request, series_id):
        # Show episodes for a specific series
        series = get_object_or_404(Series, series_id=series_id)
        episodes = Episode.objects.filter(series=series).order_by('episode_number')
        return render(request, 'admin/manage_episode.html', {
            'series': series,
            'episodes': episodes,
        })
    
class AddEpisodeView(View):
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

class EditEpisodeView(View):
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

class DeleteEpisodeView(View):
    def post(self, request, episode_id):
        episode = get_object_or_404(Episode, episode_id=episode_id)
        series_id = episode.series.series_id
        episode.delete()
        # Redirect back to the episode list for the parent series
        return redirect('manage_episode', series_id=series_id)

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
