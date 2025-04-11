# systems/urls.py

from django.urls import path
from . import views

app_name = 'systems'

urlpatterns = [
    path('', views.system_list, name='list'),
    path('<int:pk>/', views.system_detail, name='detail'),
    path('create/', views.system_create, name='create'),
    path('<int:pk>/update/', views.system_update, name='update'),
    path('<int:pk>/delete/', views.system_delete, name='delete'),
    path('relationships/', views.relationship_diagram, name='relationship_diagram'),
    path('api/relationships/', views.relationship_data, name='relationship_data'),
    path('<int:system_pk>/notes/<int:note_pk>/edit/', views.edit_system_note, name='edit_note'),
    path('<int:system_pk>/notes/<int:note_pk>/delete/', views.delete_system_note, name='delete_note'),
    path('<int:pk>/save_relationships/', views.save_system_relationships, name='save_relationships'),
]