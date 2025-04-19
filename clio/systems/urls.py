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
    
    # API endpoints for quick-edit functionality
    path('<int:pk>/update-quick/', views.quick_update_system, name='quick_update_system'),
    
    # System notes management
    path('<int:system_pk>/notes/<int:note_pk>/edit/', views.edit_system_note, name='edit_note'),
    path('<int:system_pk>/notes/<int:note_pk>/delete/', views.delete_system_note, name='delete_note'),
    
    # System relationship management
    path('<int:pk>/save_relationships/', views.save_system_relationships, name='save_relationships'),
    
    # System administrator management
    path('<int:system_pk>/administrators/add/', views.add_system_administrator, name='add_administrator'),
    path('<int:system_pk>/administrators/remove/', views.remove_system_administrator, name='remove_administrator'),
    path('administrators/<int:admin_pk>/', views.get_administrator_details, name='administrator_details'),
    
    # Category and Status management
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    path('statuses/', views.status_list, name='status_list'),
    path('statuses/create/', views.status_create, name='status_create'),
    path('statuses/<int:pk>/update/', views.status_update, name='status_update'),
    path('statuses/<int:pk>/delete/', views.status_delete, name='status_delete'),
    
    # SSO System views
    path('by-sso/<int:sso_id>/', views.systems_by_sso, name='systems_by_sso'),
    path('by-host/<int:host_id>/', views.systems_by_host, name='systems_by_host'),

    path('<int:pk>/disaster-analysis/', views.system_disaster_analysis, name='disaster_analysis'),
    path('api/<int:pk>/affected-systems/', views.get_affected_systems, name='get_affected_systems'),

    # Recovery step planning
    path('<int:system_pk>/recovery-step/', views.save_recovery_step, name='save_recovery_step'),
    path('recovery-step/<int:step_id>/', views.get_recovery_step, name='get_recovery_step'),
    path('<int:system_pk>/recovery-step/<int:step_id>/delete/', views.delete_recovery_step, name='delete_recovery_step'),
    path('<int:system_pk>/move-recovery-step/', views.move_recovery_step, name='move_recovery_step'),
]