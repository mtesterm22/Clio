# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, F
from systems.models import System, SystemRelationship, SystemCategory, SystemStatus
from scripts.models import Script, ScriptSystemRelationship
from workflows.models import Workflow
from planning.models import Initiative, Plan, Milestone, Task, ResourceAllocation

def root_redirect(request):
    """Redirect based on authentication status"""
    if request.user.is_authenticated:
        return redirect('core:index')
    else:
        return redirect('login')  # This uses Django's auth system login URL

@login_required
def index(request):
    """Dashboard view with overview of all items"""
    
    # Get active systems count using the status model
    try:
        active_status = SystemStatus.objects.get(slug='active')
        active_systems_count = System.objects.filter(status=active_status).count()
    except SystemStatus.DoesNotExist:
        active_systems_count = 0
    
    # Get deprecated systems count using the status model
    try:
        deprecated_status = SystemStatus.objects.get(slug='deprecated')
        deprecated_systems_count = System.objects.filter(status=deprecated_status).count()
    except SystemStatus.DoesNotExist:
        deprecated_systems_count = 0
    
    # Get recent systems with their related category and status
    recent_systems = System.objects.all().select_related('category', 'status').order_by('-updated_at')[:5]
    
    # Get system counts by category
    category_counts = []
    for category in SystemCategory.objects.all().order_by('order', 'name'):
        count = System.objects.filter(category=category).count()
        category_counts.append({
            'name': category.name,
            'count': count,
            'color': category.color,
            'text_color': category.text_color,
            'slug': category.slug
        })
    
    # Get system counts by status
    status_counts = []
    for status in SystemStatus.objects.all().order_by('order', 'name'):
        count = System.objects.filter(status=status).count()
        status_counts.append({
            'name': status.name,
            'count': count,
            'color': status.color,
            'text_color': status.text_color,
            'slug': status.slug,
            'is_active': status.is_active
        })
    
    context = {
        'system_count': System.objects.count(),
        'workflow_count': Workflow.objects.count(),
        'script_count': Script.objects.count(),
        'recent_systems': recent_systems,
        'recent_workflows': Workflow.objects.all().order_by('-updated_at')[:5],
        'recent_scripts': Script.objects.all().order_by('-updated_at')[:5],
        'active_systems': active_systems_count,
        'deprecated_systems': deprecated_systems_count,
        'category_counts': category_counts,
        'status_counts': status_counts,
    }
    return render(request, 'core/index.html', context)

@login_required
def about(request):
    """About page with information about the app"""
    return render(request, 'core/about.html')