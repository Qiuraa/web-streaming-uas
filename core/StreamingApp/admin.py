from django.contrib import admin
from .models import Producer, Series, SeriesGenre, Genre, User, WatchHistory


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    readonly_fields = ('producer_id', 'created_at', 'updated_at')


class SeriesGenreInline(admin.TabularInline):
    """Inline to edit the through model between Series and Genre.

    Because `Series.genre` uses `through='SeriesGenre'`, the default
    M2M widget is not available. An inline for the through model lets
    admins add/remove genres on a Series edit page.
    """
    model = SeriesGenre
    extra = 1


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    readonly_fields = ('series_id', 'created_at', 'updated_at')
    # show title and a human-friendly comma-separated genre column in the list view
    list_display = ('title', 'get_genres', 'series_id', 'created_at')
    inlines = [SeriesGenreInline]

    def get_genres(self, obj):
        # use the related manager to collect genre names
        return ", ".join([g.name for g in obj.genre.all()])

    get_genres.short_description = 'Genres'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('user_id', 'created_at', 'updated_at')
    list_display = ('username', 'email', 'role', 'user_id', 'created_at')

@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('watch_history_id', 'last_watched_at')
    list_display = ('user', 'series', 'episode', 'progress_seconds', 'last_watched_at')