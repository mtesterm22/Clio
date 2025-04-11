# core/views.py

from django.shortcuts import render
from systems.models import System
from workflows.models import Workflow
from scripts.models import Script

def index(request):
    """Dashboard view with overview of all items"""
    context = {
        'system_count': System.objects.count(),
        'workflow_count': Workflow.objects.count(),
        'script_count': Script.objects.count(),
        'recent_systems': System.objects.all().order_by('-updated_at')[:5],
        'recent_workflows': Workflow.objects.all().order_by('-updated_at')[:5],
        'recent_scripts': Script.objects.all().order_by('-updated_at')[:5],
        'active_systems': System.objects.filter(status='active').count(),
        'deprecated_systems': System.objects.filter(status='deprecated').count(),
    }
    return render(request, 'core/index.html', context)

def about(request):
    """About page with information about the app"""
    return render(request, 'core/about.html')