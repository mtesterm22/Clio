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
    
    # New workflow designer URLs
    path('<int:pk>/designer/', views.workflow_designer, name='designer'),
    path('<int:pk>/save/', views.save_workflow, name='save_workflow'),
    path('<int:pk>/versions/', views.workflow_versions, name='versions'),
    path('<int:pk>/versions/<str:version>/', views.load_workflow_version, name='load_version'),
    path('<int:pk>/versions/<int:version>/restore/', views.restore_workflow_version, name='restore_version'),
]