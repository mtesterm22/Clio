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
]