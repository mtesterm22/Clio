# planning/urls.py

from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Initiatives
    path('initiatives/', views.initiative_list, name='initiative_list'),
    path('initiatives/create/', views.initiative_create, name='initiative_create'),
    path('initiatives/<int:pk>/', views.initiative_detail, name='initiative_detail'),
    path('initiatives/<int:pk>/update/', views.initiative_update, name='initiative_update'),
    path('initiatives/<int:pk>/delete/', views.initiative_delete, name='initiative_delete'),
    
    # Plans
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:pk>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:pk>/update/', views.plan_update, name='plan_update'),
    path('plans/<int:pk>/delete/', views.plan_delete, name='plan_delete'),
    
    # Milestones
    path('plans/<int:plan_pk>/milestones/create/', views.milestone_create, name='milestone_create'),
    path('milestones/<int:pk>/update/', views.milestone_update, name='milestone_update'),
    path('milestones/<int:pk>/delete/', views.milestone_delete, name='milestone_delete'),
    
    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('plans/<int:plan_pk>/tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    
    # Resource allocations
    path('initiatives/<int:initiative_pk>/resources/create/', views.resource_allocation_create, name='resource_allocation_create'),
    path('resources/<int:pk>/update/', views.resource_allocation_update, name='resource_allocation_update'),
    path('resources/<int:pk>/delete/', views.resource_allocation_delete, name='resource_allocation_delete'),
    
    # Risks
    path('initiatives/<int:initiative_pk>/risks/create/', views.risk_create, name='risk_create'),
    path('risks/<int:pk>/update/', views.risk_update, name='risk_update'),
    path('risks/<int:pk>/delete/', views.risk_delete, name='risk_delete'),
    
    # Documents
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/initiative-status/', views.initiative_status_report, name='initiative_status_report'),
    path('reports/resource-utilization/', views.resource_utilization_report, name='resource_utilization_report'),
    path('reports/timeline-adherence/', views.timeline_adherence_report, name='timeline_adherence_report'),
]