# core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('visualizations/', views.visualization_hub, name='visualization_hub'),
    path('api/visualizations/system-script-relationships/', views.api_system_script_relationships, name='api_system_script_relationships'),
    path('api/visualizations/host-script-relationships/', views.api_host_script_relationships, name='api_host_script_relationships'),
    path('api/visualizations/workflow-plan-timeline/', views.api_workflow_plan_timeline, name='api_workflow_plan_timeline'),
    path('about/', views.about, name='about'),
]