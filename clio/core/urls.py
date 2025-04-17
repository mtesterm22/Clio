# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Changed from '' to 'index/' to avoid conflicts
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
]