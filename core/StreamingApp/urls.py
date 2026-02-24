from django.urls import path
from . import views

urlpatterns = [
    path('dashboard-admin/', views.admin_homepage, name='admin_homepage'),
    path('dashboard-admin/manage-producer/', views.manage_producer, name='manage_producer'),
    path('dashboard-admin/manage-producer/edit/<uuid:producer_id>/', views.edit_producer, name='edit_producer'),
    path('dashboard-admin/manage-studio/', views.manage_studio, name='manage_studio'),
    path('dashboard-admin/manage-producer/add/', views.add_producer, name='add_producer'),
    path('dashboard-admin/add-studio/', views.add_studio, name='add_studio'),
    # path('dashboard-admin/add-film/', views.add_film, name='add_film'),
]