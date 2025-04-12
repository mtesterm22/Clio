# planning/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q

from .models import (
    Initiative, Plan, Milestone, Task, 
    ResourceAllocation, RiskRegister, PlanningDocument
)
from .forms import (
    InitiativeForm, PlanForm, MilestoneForm, TaskForm, 
    ResourceAllocationForm, RiskRegisterForm, PlanningDocumentForm
)

@login_required
def dashboard(request):
    """Main planning dashboard showing key metrics and recent items"""
    # Get initiative counts by status
    initiative_counts = Initiative.objects.values('status').annotate(count=Count('id'))
    
    # Get task counts by status
    task_counts = Task.objects.values('status').annotate(count=Count('id'))
    
    # Get my assigned tasks
    my_tasks = Task.objects.filter(assigned_to=request.user).order_by('due_date')
    
    # Get upcoming milestones
    upcoming_milestones = Milestone.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__isnull=False
    ).order_by('due_date')[:5]
    
    # Get recent initiatives
    recent_initiatives = Initiative.objects.all().order_by('-updated_at')[:5]
    
    context = {
        'initiative_counts': initiative_counts,
        'task_counts': task_counts,
        'my_tasks': my_tasks,
        'upcoming_milestones': upcoming_milestones,
        'recent_initiatives': recent_initiatives,
    }
    
    return render(request, 'planning/dashboard.html', context)

@login_required
def initiative_list(request):
    """View to list all initiatives with filtering options"""
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    initiatives = Initiative.objects.all()
    
    # Apply filters if provided
    if status_filter:
        initiatives = initiatives.filter(status=status_filter)
    if priority_filter:
        initiatives = initiatives.filter(priority=priority_filter)
    
    # Count plans, milestones, and tasks for each initiative
    for initiative in initiatives:
        initiative.plan_count = Plan.objects.filter(initiative=initiative).count()
        initiative.task_count = Task.objects.filter(plan__initiative=initiative).count()
        initiative.risk_count = RiskRegister.objects.filter(initiative=initiative).count()
    
    context = {
        'initiatives': initiatives,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Initiative.STATUS_CHOICES,
        'priority_choices': Initiative.PRIORITY_CHOICES,
    }
    
    return render(request, 'planning/initiative_list.html', context)

@login_required
def initiative_detail(request, pk):
    """View details of an initiative"""
    initiative = get_object_or_404(Initiative, pk=pk)
    
    # Get related plans
    plans = Plan.objects.filter(initiative=initiative)
    
    # Get milestones for this initiative
    milestones = Milestone.objects.filter(plan__initiative=initiative).order_by('due_date')
    
    # Get tasks for this initiative
    tasks = Task.objects.filter(plan__initiative=initiative)
    
    # Get resource allocations
    resources = ResourceAllocation.objects.filter(initiative=initiative)
    
    # Get risks
    risks = RiskRegister.objects.filter(initiative=initiative)
    
    # Get documents
    documents = PlanningDocument.objects.filter(initiative=initiative)
    
    context = {
        'initiative': initiative,
        'plans': plans,
        'milestones': milestones,
        'tasks': tasks,
        'resources': resources,
        'risks': risks,
        'documents': documents,
    }
    
    return render(request, 'planning/initiative_detail.html', context)

@login_required
def initiative_create(request):
    """Create a new initiative"""
    if request.method == 'POST':
        form = InitiativeForm(request.POST)
        if form.is_valid():
            initiative = form.save()
            messages.success(request, f'Initiative "{initiative.name}" was created successfully.')
            return redirect('planning:initiative_detail', pk=initiative.pk)
    else:
        form = InitiativeForm()
    
    return render(request, 'planning/initiative_form.html', {
        'form': form, 
        'title': 'Create Initiative'
    })

@login_required
def initiative_update(request, pk):
    """Update an existing initiative"""
    initiative = get_object_or_404(Initiative, pk=pk)
    
    if request.method == 'POST':
        form = InitiativeForm(request.POST, instance=initiative)
        if form.is_valid():
            form.save()
            messages.success(request, f'Initiative "{initiative.name}" was updated successfully.')
            return redirect('planning:initiative_detail', pk=initiative.pk)
    else:
        form = InitiativeForm(instance=initiative)
    
    return render(request, 'planning/initiative_form.html', {
        'form': form, 
        'initiative': initiative,
        'title': 'Update Initiative'
    })

@login_required
def initiative_delete(request, pk):
    """Delete an initiative"""
    initiative = get_object_or_404(Initiative, pk=pk)
    
    if request.method == 'POST':
        initiative_name = initiative.name
        initiative.delete()
        messages.success(request, f'Initiative "{initiative_name}" was deleted successfully.')
        return redirect('planning:initiative_list')
    
    return render(request, 'planning/initiative_confirm_delete.html', {
        'initiative': initiative
    })