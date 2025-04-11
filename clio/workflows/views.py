# workflows/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Workflow, WorkflowStep, WorkflowDocument
from .forms import WorkflowForm, WorkflowStepForm, WorkflowDocumentForm
from systems.models import System

def workflow_list(request):
    """View to list all workflows"""
    status_filter = request.GET.get('status')
    
    workflows = Workflow.objects.all()
    
    if status_filter:
        workflows = workflows.filter(status=status_filter)
    
    context = {
        'workflows': workflows,
        'status_filter': status_filter,
        'status_choices': Workflow.STATUS_CHOICES,
    }
    
    return render(request, 'workflows/workflow_list.html', context)

def workflow_detail(request, pk):
    """View details of a workflow"""
    workflow = get_object_or_404(Workflow, pk=pk)
    
    # Get the documents
    documents = workflow.documents.all()
    
    # Get workflow steps
    steps = workflow.steps.all().order_by('order')
    
    # Get associated systems
    systems = workflow.systems.all()
    
    # Get associated scripts
    scripts = workflow.scripts.all()
    
    context = {
        'workflow': workflow,
        'documents': documents,
        'steps': steps,
        'systems': systems,
        'scripts': scripts,
    }
    
    return render(request, 'workflows/workflow_detail.html', context)

def workflow_create(request):
    """Create a new workflow"""
    if request.method == 'POST':
        form = WorkflowForm(request.POST)
        if form.is_valid():
            workflow = form.save()
            messages.success(request, f'Workflow "{workflow.name}" was created successfully.')
            return redirect('workflows:detail', pk=workflow.pk)
    else:
        form = WorkflowForm()
    
    return render(request, 'workflows/workflow_form.html', {'form': form, 'title': 'Create Workflow'})

def workflow_update(request, pk):
    """Update an existing workflow"""
    workflow = get_object_or_404(Workflow, pk=pk)
    
    if request.method == 'POST':
        form = WorkflowForm(request.POST, instance=workflow)
        if form.is_valid():
            form.save()
            messages.success(request, f'Workflow "{workflow.name}" was updated successfully.')
            return redirect('workflows:detail', pk=workflow.pk)
    else:
        form = WorkflowForm(instance=workflow)
    
    return render(request, 'workflows/workflow_form.html', {'form': form, 'workflow': workflow, 'title': 'Update Workflow'})

def workflow_delete(request, pk):
    """Delete a workflow"""
    workflow = get_object_or_404(Workflow, pk=pk)
    
    if request.method == 'POST':
        workflow_name = workflow.name
        workflow.delete()
        messages.success(request, f'Workflow "{workflow_name}" was deleted successfully.')
        return redirect('workflows:list')
    
    return render(request, 'workflows/workflow_confirm_delete.html', {'workflow': workflow})

def add_workflow_step(request, pk):
    """Add a step to a workflow"""
    workflow = get_object_or_404(Workflow, pk=pk)
    
    if request.method == 'POST':
        form = WorkflowStepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.workflow = workflow
            
            # Set order to last + 1
            last_order = workflow.steps.order_by('-order').first()
            step.order = 1 if not last_order else last_order.order + 1
            
            step.save()
            messages.success(request, f'Step "{step.name}" was added to the workflow.')
            return redirect('workflows:detail', pk=workflow.pk)
    else:
        form = WorkflowStepForm()
    
    return render(request, 'workflows/step_form.html', {
        'form': form, 
        'workflow': workflow, 
        'title': 'Add Workflow Step'
    })

def update_workflow_step(request, pk):
    """Update a workflow step"""
    step = get_object_or_404(WorkflowStep, pk=pk)
    workflow = step.workflow
    
    if request.method == 'POST':
        form = WorkflowStepForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            messages.success(request, f'Step "{step.name}" was updated successfully.')
            return redirect('workflows:detail', pk=workflow.pk)
    else:
        form = WorkflowStepForm(instance=step)
    
    return render(request, 'workflows/step_form.html', {
        'form': form, 
        'workflow': workflow, 
        'step': step,
        'title': 'Update Workflow Step'
    })

def delete_workflow_step(request, pk):
    """Delete a workflow step"""
    step = get_object_or_404(WorkflowStep, pk=pk)
    workflow = step.workflow
    
    if request.method == 'POST':
        step_name = step.name
        
        # Reorder remaining steps
        steps_to_update = workflow.steps.filter(order__gt=step.order)
        for later_step in steps_to_update:
            later_step.order -= 1
            later_step.save()
            
        step.delete()
        messages.success(request, f'Step "{step_name}" was deleted from the workflow.')
        return redirect('workflows:detail', pk=workflow.pk)
    
    return render(request, 'workflows/step_confirm_delete.html', {
        'step': step,
        'workflow': workflow
    })