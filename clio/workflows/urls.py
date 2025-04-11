# workflows/urls.py

from django.urls import path
from . import views

app_name = 'workflows'

urlpatterns = [
    path('', views.workflow_list, name='list'),
    path('<int:pk>/', views.workflow_detail, name='detail'),
    path('create/', views.workflow_create, name='create'),
    path('<int:pk>/update/', views.workflow_update, name='update'),
    path('<int:pk>/delete/', views.workflow_delete, name='delete'),
    path('<int:pk>/add_step/', views.add_workflow_step, name='add_step'),
    path('step/<int:pk>/update/', views.update_workflow_step, name='update_step'),
    path('step/<int:pk>/delete/', views.delete_workflow_step, name='delete_step'),
    path('step/<int:pk>/reorder/', views.reorder_workflow_step, name='reorder_step'),
]