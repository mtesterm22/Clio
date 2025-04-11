# scripts/urls.py

from django.urls import path
from . import views

app_name = 'scripts'

urlpatterns = [
    path('', views.script_list, name='list'),
    path('<int:pk>/', views.script_detail, name='detail'),
    path('create/', views.script_create, name='create'),
    path('<int:pk>/update/', views.script_update, name='update'),
    path('<int:pk>/delete/', views.script_delete, name='delete'),
    
    # System relationship management
    path('<int:script_pk>/relationship/<int:relationship_pk>/update/', 
         views.update_system_relationship, name='update_relationship'),
    path('<int:script_pk>/relationship/<int:relationship_pk>/delete/', 
         views.delete_system_relationship, name='delete_relationship'),
]