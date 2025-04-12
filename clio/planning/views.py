# planning/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, Case, When, Value, IntegerField, F
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import User

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

# Initiative Views
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
            return redirect('initiative_detail', pk=initiative.pk)
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
            return redirect('initiative_detail', pk=initiative.pk)
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
        return redirect('initiative_list')
    
    return render(request, 'planning/initiative_confirm_delete.html', {
        'initiative': initiative
    })

# Plan Views
@login_required
def plan_list(request):
    """View to list all plans with filtering options"""
    status_filter = request.GET.get('status')
    initiative_filter = request.GET.get('initiative')
    
    plans = Plan.objects.all()
    
    # Apply filters if provided
    if status_filter:
        plans = plans.filter(status=status_filter)
    if initiative_filter:
        plans = plans.filter(initiative_id=initiative_filter)
    
    # Get all initiatives for the filter dropdown
    initiatives = Initiative.objects.all()
    
    # Add task completion info
    for plan in plans:
        plan.tasks.completed = plan.tasks.filter(status='completed')
    
    context = {
        'plans': plans,
        'status_filter': status_filter,
        'initiative_filter': initiative_filter,
        'status_choices': Plan.STATUS_CHOICES,
        'initiatives': initiatives,
    }
    
    return render(request, 'planning/plan_list.html', context)

@login_required
def plan_detail(request, pk):
    """View details of a plan"""
    plan = get_object_or_404(Plan, pk=pk)
    
    # Get milestones for this plan
    milestones = Milestone.objects.filter(plan=plan).order_by('due_date')
    
    # Get tasks for this plan
    tasks = Task.objects.filter(plan=plan)
    
    # Get resource allocations for this plan
    resources = ResourceAllocation.objects.filter(plan=plan)
    
    # Get documents for this plan
    documents = PlanningDocument.objects.filter(plan=plan)
    
    # Calculate completion percentage
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    
    completion_percentage = 0
    if total_tasks > 0:
        completion_percentage = int((completed_tasks / total_tasks) * 100)
    
    context = {
        'plan': plan,
        'milestones': milestones,
        'tasks': tasks,
        'resources': resources,
        'documents': documents,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_percentage': completion_percentage,
    }
    
    return render(request, 'planning/plan_detail.html', context)

@login_required
def plan_create(request):
    """Create a new plan"""
    initiative_id = request.GET.get('initiative')
    initiative = None
    
    if initiative_id:
        initiative = get_object_or_404(Initiative, pk=initiative_id)
    
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()
            messages.success(request, f'Plan "{plan.name}" was created successfully.')
            return redirect('plan_detail', pk=plan.pk)
    else:
        initial = {}
        if initiative:
            initial['initiative'] = initiative
        
        form = PlanForm(initial=initial)
    
    return render(request, 'planning/plan_form.html', {
        'form': form, 
        'title': 'Create Plan',
        'initiative': initiative
    })

@login_required
def plan_update(request, pk):
    """Update an existing plan"""
    plan = get_object_or_404(Plan, pk=pk)
    
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plan "{plan.name}" was updated successfully.')
            return redirect('plan_detail', pk=plan.pk)
    else:
        form = PlanForm(instance=plan)
    
    return render(request, 'planning/plan_form.html', {
        'form': form, 
        'plan': plan,
        'title': 'Update Plan'
    })

@login_required
def plan_delete(request, pk):
    """Delete a plan"""
    plan = get_object_or_404(Plan, pk=pk)
    
    if request.method == 'POST':
        initiative = plan.initiative
        plan_name = plan.name
        plan.delete()
        messages.success(request, f'Plan "{plan_name}" was deleted successfully.')
        return redirect('initiative_detail', pk=initiative.pk)
    
    return render(request, 'planning/plan_confirm_delete.html', {
        'plan': plan
    })

# Milestone Views
@login_required
def milestone_create(request, plan_pk):
    """Create a new milestone for a specific plan"""
    plan = get_object_or_404(Plan, pk=plan_pk)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.plan = plan
            milestone.save()
            
            # Handle many-to-many dependencies after saving
            if form.cleaned_data.get('dependencies'):
                form.save_m2m()
                
            messages.success(request, f'Milestone "{milestone.name}" was created successfully.')
            return redirect('plan_detail', pk=plan.pk)
    else:
        form = MilestoneForm()
    
    return render(request, 'planning/milestone_form.html', {
        'form': form, 
        'plan': plan,
        'title': 'Create Milestone'
    })

@login_required
def milestone_update(request, pk):
    """Update an existing milestone"""
    milestone = get_object_or_404(Milestone, pk=pk)
    plan = milestone.plan
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, f'Milestone "{milestone.name}" was updated successfully.')
            return redirect('plan_detail', pk=plan.pk)
    else:
        form = MilestoneForm(instance=milestone)
    
    return render(request, 'planning/milestone_form.html', {
        'form': form, 
        'milestone': milestone,
        'plan': plan,
        'title': 'Update Milestone'
    })

@login_required
def milestone_delete(request, pk):
    """Delete a milestone"""
    milestone = get_object_or_404(Milestone, pk=pk)
    plan = milestone.plan
    
    if request.method == 'POST':
        milestone_name = milestone.name
        milestone.delete()
        messages.success(request, f'Milestone "{milestone_name}" was deleted successfully.')
        return redirect('plan_detail', pk=plan.pk)
    
    return render(request, 'planning/milestone_confirm_delete.html', {
        'milestone': milestone,
        'plan': plan
    })

# Task Views
@login_required
def task_list(request):
    """View to list all tasks with filtering options"""
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    plan_filter = request.GET.get('plan')
    assigned_filter = request.GET.get('assigned_to')
    milestone_filter = request.GET.get('milestone')
    
    tasks = Task.objects.all()
    
    # Apply filters if provided
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if plan_filter:
        tasks = tasks.filter(plan_id=plan_filter)
    if assigned_filter:
        if assigned_filter == 'me':
            tasks = tasks.filter(assigned_to=request.user)
        elif assigned_filter == 'unassigned':
            tasks = tasks.filter(assigned_to__isnull=True)
        else:
            tasks = tasks.filter(assigned_to_id=assigned_filter)
    if milestone_filter:
        tasks = tasks.filter(milestone_id=milestone_filter)
    
    # Prepare filter choices
    plans = Plan.objects.all()
    milestones = Milestone.objects.all()
    assignees = User.objects.filter(assigned_tasks__isnull=False).distinct()
    
    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'plan_filter': plan_filter,
        'assigned_filter': assigned_filter,
        'milestone_filter': milestone_filter,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'plans': plans,
        'milestones': milestones,
        'assignees': assignees
    }
    
    return render(request, 'planning/task_list.html', context)

@login_required
def task_detail(request, pk):
    """View details of a task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Get documents for this task
    documents = PlanningDocument.objects.filter(task=task)
    
    context = {
        'task': task,
        'documents': documents,
    }
    
    return render(request, 'planning/task_detail.html', context)

@login_required
def task_create(request, plan_pk):
    """Create a new task for a specific plan"""
    plan = get_object_or_404(Plan, pk=plan_pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.plan = plan
            task.save()
            
            # Handle many-to-many relationships after saving
            form.save_m2m()
            
            messages.success(request, f'Task "{task.name}" was created successfully.')
            return redirect('plan_detail', pk=plan.pk)
    else:
        initial = {'plan': plan}
        form = TaskForm(initial=initial)
        # Limit milestone choices to this plan
        form.fields['milestone'].queryset = Milestone.objects.filter(plan=plan)
    
    return render(request, 'planning/task_form.html', {
        'form': form, 
        'plan': plan,
        'title': 'Create Task'
    })

@login_required
def task_update(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk)
    plan = task.plan
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.name}" was updated successfully.')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
        # Limit milestone choices to this plan
        form.fields['milestone'].queryset = Milestone.objects.filter(plan=plan)
    
    return render(request, 'planning/task_form.html', {
        'form': form, 
        'task': task,
        'plan': plan,
        'title': 'Update Task'
    })

@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk)
    plan = task.plan
    
    if request.method == 'POST':
        task_name = task.name
        task.delete()
        messages.success(request, f'Task "{task_name}" was deleted successfully.')
        return redirect('planning_plan_detail', pk=plan.pk)
    
    return render(request, 'planning/task_confirm_delete.html', {
        'task': task,
        'plan': plan
    })

# Resource Allocation Views
@login_required
def resource_allocation_create(request, initiative_pk):
    """Create a new resource allocation for a specific initiative"""
    initiative = get_object_or_404(Initiative, pk=initiative_pk)
    
    if request.method == 'POST':
        form = ResourceAllocationForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.initiative = initiative
            resource.save()
            messages.success(request, f'Resource allocation for {resource.user.get_full_name() or resource.user.username} was created successfully.')
            return redirect('initiative_detail', pk=initiative.pk)
    else:
        form = ResourceAllocationForm(initial={'initiative': initiative})
    
    return render(request, 'planning/resource_allocation_form.html', {
        'form': form, 
        'initiative': initiative,
        'title': 'Add Resource Allocation'
    })

@login_required
def resource_allocation_update(request, pk):
    """Update an existing resource allocation"""
    resource = get_object_or_404(ResourceAllocation, pk=pk)
    initiative = resource.initiative
    
    if request.method == 'POST':
        form = ResourceAllocationForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, f'Resource allocation for {resource.user.get_full_name() or resource.user.username} was updated successfully.')
            if initiative:
                return redirect('initiative_detail', pk=initiative.pk)
            else:
                return redirect('plan_detail', pk=resource.plan.pk)
    else:
        form = ResourceAllocationForm(instance=resource)
    
    return render(request, 'planning/resource_allocation_form.html', {
        'form': form, 
        'resource': resource,
        'initiative': initiative,
        'title': 'Update Resource Allocation'
    })

@login_required
def resource_allocation_delete(request, pk):
    """Delete a resource allocation"""
    resource = get_object_or_404(ResourceAllocation, pk=pk)
    initiative = resource.initiative
    plan = resource.plan
    
    if request.method == 'POST':
        resource_name = f"{resource.user.get_full_name() or resource.user.username} - {resource.role}"
        resource.delete()
        messages.success(request, f'Resource allocation for {resource_name} was deleted successfully.')
        
        if initiative:
            return redirect('initiative_detail', pk=initiative.pk)
        else:
            return redirect('plan_detail', pk=plan.pk)
    
    return render(request, 'planning/resource_allocation_confirm_delete.html', {
        'resource': resource,
        'initiative': initiative,
        'plan': plan
    })

# Risk Views
@login_required
def risk_create(request, initiative_pk):
    """Create a new risk for a specific initiative"""
    initiative = get_object_or_404(Initiative, pk=initiative_pk)
    
    if request.method == 'POST':
        form = RiskRegisterForm(request.POST)
        if form.is_valid():
            risk = form.save(commit=False)
            risk.initiative = initiative
            risk.save()
            messages.success(request, 'Risk was added successfully.')
            return redirect('initiative_detail', pk=initiative.pk)
    else:
        form = RiskRegisterForm(initial={'initiative': initiative})
    
    return render(request, 'planning/risk_form.html', {
        'form': form, 
        'initiative': initiative,
        'title': 'Add Risk'
    })

@login_required
def risk_update(request, pk):
    """Update an existing risk"""
    risk = get_object_or_404(RiskRegister, pk=pk)
    initiative = risk.initiative
    
    if request.method == 'POST':
        form = RiskRegisterForm(request.POST, instance=risk)
        if form.is_valid():
            form.save()
            messages.success(request, 'Risk was updated successfully.')
            return redirect('initiative_detail', pk=initiative.pk)
    else:
        form = RiskRegisterForm(instance=risk)
    
    return render(request, 'planning/risk_form.html', {
        'form': form, 
        'risk': risk,
        'initiative': initiative,
        'title': 'Update Risk'
    })

@login_required
def risk_delete(request, pk):
    """Delete a risk"""
    risk = get_object_or_404(RiskRegister, pk=pk)
    initiative = risk.initiative
    
    if request.method == 'POST':
        risk.delete()
        messages.success(request, 'Risk was deleted successfully.')
        return redirect('planning_initiative_detail', pk=initiative.pk)
    
    return render(request, 'planning/risk_confirm_delete.html', {
        'risk': risk,
        'initiative': initiative
    })

# Document Views
@login_required
def document_upload(request):
    """Upload a new planning document"""
    initiative_id = request.GET.get('initiative')
    plan_id = request.GET.get('plan')
    task_id = request.GET.get('task')
    
    initiative = None
    plan = None
    task = None
    
    if initiative_id:
        initiative = get_object_or_404(Initiative, pk=initiative_id)
    if plan_id:
        plan = get_object_or_404(Plan, pk=plan_id)
    if task_id:
        task = get_object_or_404(Task, pk=task_id)
    
    if request.method == 'POST':
        form = PlanningDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.created_by = request.user
            
            # Assign to appropriate parent
            if initiative_id:
                document.initiative_id = initiative_id
            if plan_id:
                document.plan_id = plan_id
            if task_id:
                document.task_id = task_id
                
            document.save()
            messages.success(request, f'Document "{document.name}" was uploaded successfully.')
            
            # Redirect based on context
            if task:
                return redirect('task_detail', pk=task.pk)
            elif plan:
                return redirect('plan_detail', pk=plan.pk)
            elif initiative:
                return redirect('initiative_detail', pk=initiative.pk)
            else:
                return redirect('dashboard')
    else:
        initial = {}
        if initiative:
            initial['initiative'] = initiative
        if plan:
            initial['plan'] = plan
        if task:
            initial['task'] = task
        
        form = PlanningDocumentForm(initial=initial)
    
    context = {
        'form': form,
        'initiative': initiative,
        'plan': plan,
        'task': task,
        'title': 'Upload Document'
    }
    
    return render(request, 'planning/document_form.html', context)

@login_required
def document_delete(request, pk):
    """Delete a document"""
    document = get_object_or_404(PlanningDocument, pk=pk)
    
    # Store references before deleting
    initiative = document.initiative
    plan = document.plan
    task = document.task
    
    if request.method == 'POST':
        document_name = document.name
        document.delete()
        messages.success(request, f'Document "{document_name}" was deleted successfully.')
        
        # Redirect based on context
        if task:
            return redirect('task_detail', pk=task.pk)
        elif plan:
            return redirect('planning_plan_detail', pk=plan.pk)
        elif initiative:
            return redirect('initiative_detail', pk=initiative.pk)
        else:
            return redirect('dashboard')
    
    context = {
        'document': document,
        'initiative': initiative,
        'plan': plan,
        'task': task
    }
    
    return render(request, 'planning/document_confirm_delete.html', context)

# Report Views
@login_required
def reports(request):
    """Main reports landing page"""
    context = {}
    return render(request, 'planning/reports/index.html', context)

@login_required
def initiative_status_report(request):
    """Report showing initiative status breakdown"""
    # Get initiative counts by status
    status_counts = Initiative.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    # Get initiative counts by priority
    priority_counts = Initiative.objects.values('priority').annotate(count=Count('id')).order_by('priority')
    
    # Get owners with most initiatives
    top_owners = Initiative.objects.exclude(owner__isnull=True).values('owner__username', 'owner__first_name', 'owner__last_name').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Get completion percentage for each initiative
    initiatives = Initiative.objects.all()
    for initiative in initiatives:
        total_tasks = Task.objects.filter(plan__initiative=initiative).count()
        completed_tasks = Task.objects.filter(plan__initiative=initiative, status='completed').count()
        
        if total_tasks > 0:
            initiative.completion_percentage = int((completed_tasks / total_tasks) * 100)
        else:
            initiative.completion_percentage = 0
    
    context = {
        'status_counts': status_counts,
        'priority_counts': priority_counts,
        'top_owners': top_owners,
        'initiatives': initiatives
    }
    
    return render(request, 'planning/reports/initiative_status.html', context)

@login_required
def resource_utilization_report(request):
    """Report showing resource allocation and utilization"""
    # Get all resource allocations
    allocations = ResourceAllocation.objects.all()
    
    # Calculate total allocation percentage per user
    users_allocation = User.objects.filter(resource_allocations__isnull=False).distinct()
    
    for user in users_allocation:
        # Check current allocations (those that are active now)
        current_date = timezone.now().date()
        current_allocations = ResourceAllocation.objects.filter(
            user=user,
            start_date__lte=current_date,
            end_date__gte=current_date
        )
        
        user.total_allocation = current_allocations.aggregate(Sum('allocation_percentage'))['allocation_percentage__sum'] or 0
        user.allocation_count = current_allocations.count()
        
        # Check if over-allocated
        user.is_over_allocated = user.total_allocation > 100
    
    # Get initiatives with most resources allocated
    top_initiatives = Initiative.objects.annotate(
        resource_count=Count('resource_allocations', distinct=True)
    ).order_by('-resource_count')[:5]
    
    # Get upcoming resource changes
    upcoming_end_dates = ResourceAllocation.objects.filter(
        end_date__gt=timezone.now().date()
    ).order_by('end_date')[:10]
    
    context = {
        'users_allocation': users_allocation,
        'top_initiatives': top_initiatives,
        'upcoming_end_dates': upcoming_end_dates,
        'allocations': allocations
    }
    
    return render(request, 'planning/reports/resource_utilization.html', context)

@login_required
def timeline_adherence_report(request):
    """Report showing adherence to timelines and milestones"""
    # Get all initiatives with timeline details
    initiatives = Initiative.objects.filter(
        start_date__isnull=False,
        target_completion_date__isnull=False
    )
    
    # Calculate days behind/ahead for initiatives
    for initiative in initiatives:
        if initiative.actual_completion_date and initiative.target_completion_date:
            # Positive means ahead of schedule, negative means behind
            initiative.days_variance = (initiative.target_completion_date - initiative.actual_completion_date).days
        else:
            initiative.days_variance = 0
        
        # Calculate percentage complete based on tasks
        total_tasks = Task.objects.filter(plan__initiative=initiative).count()
        completed_tasks = Task.objects.filter(plan__initiative=initiative, status='completed').count()
        
        if total_tasks > 0:
            initiative.completion_percentage = int((completed_tasks / total_tasks) * 100)
        else:
            initiative.completion_percentage = 0
    
    # Get milestones status summary
    milestone_status = Milestone.objects.values('status').annotate(count=Count('id'))
    
    # Get milestones with approaching deadlines
    today = timezone.now().date()
    upcoming_milestones = Milestone.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__gte=today
    ).order_by('due_date')[:10]
    
    # Get milestone adherence data
    passed_milestones = Milestone.objects.filter(due_date__lt=today)
    
    on_time_count = passed_milestones.filter(
        status='completed',
        updated_at__date__lte=F('due_date')
    ).count()
    
    late_count = passed_milestones.filter(
        status='completed',
        updated_at__date__gt=F('due_date')
    ).count()
    
    missed_count = passed_milestones.filter(status='missed').count()
    
    context = {
        'initiatives': initiatives,
        'milestone_status': milestone_status,
        'upcoming_milestones': upcoming_milestones,
        'on_time_count': on_time_count,
        'late_count': late_count,
        'missed_count': missed_count,
        'total_passed': passed_milestones.count()
    }
    
    return render(request, 'planning/reports/timeline_adherence.html', context)