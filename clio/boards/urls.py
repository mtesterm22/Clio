# boards/urls.py

from django.urls import path
from . import views

app_name = 'boards'

urlpatterns = [
    # Board views
    path('', views.board_list, name='list'),
    path('create/', views.board_create, name='create'),
    path('<int:pk>/', views.board_detail, name='detail'),
    
    # Card views
    path('cards/', views.card_list, name='card_list'),
    path('cards/create/', views.card_create, name='card_create'),
    path('boards/<int:board_pk>/cards/create/', views.card_create, name='board_card_create'),
    path('cards/<int:pk>/', views.card_detail, name='card_detail'),
    path('cards/<int:pk>/update/', views.card_update, name='card_update'),
    path('cards/<int:pk>/checkout/', views.card_checkout, name='card_checkout'),
    
    # API endpoints
    path('api/cards/position/', views.save_card_position, name='save_card_position'),
    
    # Document management
    path('cards/<int:card_pk>/documents/upload/', views.upload_document, name='upload_document'),
]