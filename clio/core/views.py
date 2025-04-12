# core/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, F
from systems.models import System, SystemRelationship, SystemCategory, SystemStatus
from scripts.models import Script, ScriptSystemRelationship
from workflows.models import Workflow
from planning.models import Initiative, Plan, Milestone, Task, ResourceAllocation

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

@login_required
def visualization_hub(request):
    """Central visualization hub for various data visualizations"""
    context = {
        'title': 'Visualization Hub',
    }
    return render(request, 'core/visualization_hub.html', context)

def api_system_script_relationships(request):
    """API endpoint for system-script relationship visualization"""
    # Get all scripts with their systems
    scripts = Script.objects.prefetch_related('system_relationships__system').all()
    
    # Format the data for the visualization
    nodes = []
    links = []
    
    # Add system nodes
    systems_set = set()
    for script in scripts:
        for rel in script.system_relationships.all():
            systems_set.add(rel.system)
    
    for system in systems_set:
        nodes.append({
            'id': f"system-{system.id}",
            'type': 'system',
            'name': system.name,
            'category': {
                'slug': system.category.slug,
                'name': system.category.name,
                'color': system.category.color,
                'text_color': system.category.text_color
            } if system.category else None,
            'status': {
                'slug': system.status.slug,
                'name': system.status.name,
                'is_active': system.status.is_active
            } if system.status else None
        })
    
    # Add script nodes
    for script in scripts:
        nodes.append({
            'id': f"script-{script.id}",
            'type': 'script',
            'name': script.name,
            'language': script.programming_language,
            'schedule_method': script.schedule_method,
            'hosted_on': script.hosted_on.name if script.hosted_on else None
        })
        
        # Add links between scripts and systems
        for rel in script.system_relationships.all():
            links.append({
                'source': f"script-{script.id}",
                'target': f"system-{rel.system.id}",
                'type': rel.relationship_type,
                'description': rel.description
            })
    
    return JsonResponse({
        'nodes': nodes,
        'links': links
    })

def api_host_script_relationships(request):
    """API endpoint for host-script relationship visualization"""
    # Get all scripts with hosting information
    scripts = Script.objects.select_related('hosted_on').all()
    
    # Format the data for the visualization
    hosts = []
    scripts_data = []
    languages = []
    schedule_methods = []
    
    # Add host systems
    host_systems = System.objects.filter(hosted_scripts__isnull=False).distinct()
    for host in host_systems:
        hosts.append({
            'id': host.id,
            'name': host.name,
            'category': host.category.slug if host.category else None,
            'status': host.status.slug if host.status else None
        })
    
    # Add scripts with their hosts
    language_set = set()
    schedule_set = set()
    
    for script in scripts:
        scripts_data.append({
            'id': script.id,
            'name': script.name,
            'language': script.programming_language,
            'schedule_method': script.schedule_method,
            'host_id': script.hosted_on.id if script.hosted_on else None,
            'host_location': script.host_location
        })
        
        if script.programming_language:
            language_set.add(script.programming_language)
            
        if script.schedule_method:
            schedule_set.add(script.schedule_method)
    
    # Create language and schedule method lists
    languages = [{'name': lang} for lang in sorted(language_set)]
    schedule_methods = [{'name': method} for method in sorted(schedule_set)]
    
    return JsonResponse({
        'hosts': hosts,
        'scripts': scripts_data,
        'languages': languages,
        'schedule_methods': schedule_methods
    })

def api_workflow_plan_timeline(request):
    """API endpoint for workflow-plan timeline visualization"""
    # Get initiatives, plans, milestones
    initiatives = Initiative.objects.all()
    plans = Plan.objects.all()
    milestones = Milestone.objects.all()
    
    # Format the data for the visualization
    initiatives_data = []
    plans_data = []
    milestones_data = []
    dependencies = []
    
    # Add initiatives
    for initiative in initiatives:
        initiatives_data.append({
            'id': initiative.id,
            'name': initiative.name,
            'type': 'initiative',
            'status': initiative.status,
            'priority': initiative.priority,
            'start_date': initiative.start_date.isoformat() if initiative.start_date else None,
            'target_completion_date': initiative.target_completion_date.isoformat() if initiative.target_completion_date else None,
            'actual_completion_date': initiative.actual_completion_date.isoformat() if initiative.actual_completion_date else None
        })
    
    # Add plans
    for plan in plans:
        plans_data.append({
            'id': plan.id,
            'name': plan.name,
            'type': 'plan',
            'status': plan.status,
            'initiative_id': plan.initiative_id,
            'initiative_name': plan.initiative.name if plan.initiative else None,
            'created_at': plan.created_at.isoformat() if plan.created_at else None,
            'updated_at': plan.updated_at.isoformat() if plan.updated_at else None
        })
    
    # Add milestones
    for milestone in milestones:
        milestones_data.append({
            'id': milestone.id,
            'name': milestone.name,
            'type': 'milestone',
            'status': milestone.status,
            'plan_id': milestone.plan_id,
            'plan_name': milestone.plan.name if milestone.plan else None,
            'due_date': milestone.due_date.isoformat() if milestone.due_date else None
        })
        
        # Add dependencies between milestones
        for dep in milestone.dependencies.all():
            dependencies.append({
                'source': dep.id,
                'target': milestone.id,
                'type': 'milestone_dependency'
            })
    
    # Add initiative dependencies
    for initiative in initiatives:
        for dep in initiative.dependencies.all():
            dependencies.append({
                'source': dep.id,
                'target': initiative.id,
                'type': 'initiative_dependency'
            })
    
    return JsonResponse({
        'initiatives': initiatives_data,
        'plans': plans_data,
        'milestones': milestones_data,
        'dependencies': dependencies
    })