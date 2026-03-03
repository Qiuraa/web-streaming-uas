from django.urls import path
from . import views

urlpatterns = [
    path('dashboard-admin/', views.admin_homepage, name='admin_homepage'),
    path('dashboard-admin/manage-producer/', views.manage_producer, name='manage_producer'),
    path('dashboard-admin/manage-producer/edit/<uuid:producer_id>/', views.edit_producer, name='edit_producer'),
    path('dashboard-admin/manage-producer/delete/<uuid:producer_id>/', views.delete_producer, name='delete_producer'),
    path('dashboard-admin/manage-producer/add/', views.add_producer, name='add_producer'),
    path('dashboard-admin/manage-studio/', views.manage_studio, name='manage_studio'),
    path('dashboard-admin/manage-studio/edit/<uuid:studio_id>/', views.edit_studio, name='edit_studio'),
    path('dashboard-admin/manage-studio/delete/<uuid:studio_id>/', views.delete_studio, name='delete_studio'),
    path('dashboard-admin/manage-studio/add/', views.add_studio, name='add_studio'),
    path('dashboard-admin/manage-film/', views.manage_film, name='manage_film'),
    path('dashboard-admin/manage-film/add/', views.add_film, name='add_film'),
    path('dashboard-admin/manage-genre/', views.manage_genre, name='manage_genre'),
    path('dashboard-admin/manage-genre/add/', views.add_genre, name='add_genre'),
    path('dashboard-admin/manage-genre/edit/<uuid:genre_id>/', views.edit_genre, name='edit_genre'),
    path('dashboard-admin/manage-genre/delete/<uuid:genre_id>/', views.delete_genre, name='delete_genre'),
    path('dashboard-admin/manage-film/edit/<uuid:series_id>/', views.edit_film, name='edit_film'),
    path('dashboard-admin/manage-film/delete/<uuid:series_id>/', views.delete_film, name='delete_film'),
    path('dashboard-admin/manage-episode/<uuid:series_id>', views.manage_episode, name='manage_episode'),
    path('dashboard-admin/manage-episode/add/<uuid:series_id>/', views.add_episode, name='add_episode'),
    # Detail view shows the series and chooses the default episode (ep #1) itself,
    # so only series_id is required in the URL.
    path('dashboard-admin/manage-film/detail/<uuid:series_id>/', views.detail_film, name='detail_film'),
    path('dashboard-admin/manage-episode/edit/<uuid:episode_id>/', views.edit_episode, name='edit_episode'),
    path('dashboard-admin/manage-episode/delete/<uuid:episode_id>/', views.delete_episode, name='delete_episode'),
    path('dashboard-admin/manage-episode/play/<uuid:episode_id>/', views.play_episode, name='play_episode'),
]   