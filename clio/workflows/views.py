# workflows/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from .models import Workflow, WorkflowVersion, WorkflowDocument
from .forms import WorkflowForm, WorkflowDocumentForm
from systems.models import System
from scripts.models import Script

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
    
    # Get associated systems
    systems = workflow.systems.all()
    
    # Get associated scripts - use the new related_name
    scripts = workflow.scripts.all()
    
    # Handle document upload
    if request.method == 'POST' and request.FILES:
        form = WorkflowDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.workflow = workflow
            document.save()
            messages.success(request, f'Document "{document.name}" was uploaded successfully.')
            return redirect('workflows:detail', pk=workflow.pk)
    
    context = {
        'workflow': workflow,
        'documents': documents,
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
            
            # Initialize with start and end nodes
            nodes = [
                {
                    'id': 'start',
                    'type': 'start',
                    'position': {'x': 250, 'y': 50},
                    'data': {'label': 'Start Workflow'}
                },
                {
                    'id': 'end',
                    'type': 'end',
                    'position': {'x': 250, 'y': 300},
                    'data': {'label': 'End Workflow'}
                }
            ]
            
            # Initialize with a direct connection
            edges = [
                {
                    'id': 'e-start-end',
                    'source': 'start',
                    'target': 'end'
                }
            ]
            
            workflow.nodes = nodes
            workflow.edges = edges
            workflow.save()
            
            # Create initial version
            WorkflowVersion.objects.create(
                workflow=workflow,
                version=1,
                nodes=nodes,
                edges=edges,
                created_by=request.user if request.user.is_authenticated else None
            )
            
            messages.success(request, f'Workflow "{workflow.name}" was created successfully.')
            return redirect('workflows:designer', pk=workflow.pk)
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

def workflow_designer(request, pk):
    """Visual workflow designer interface"""
    workflow = get_object_or_404(Workflow, pk=pk)
    
    # Get all systems and scripts for the dropdown menus
    systems = System.objects.all().values('id', 'name', 'category__name', 'category__color', 'category__text_color')
    scripts = Script.objects.all().values('id', 'name', 'programming_language')
    
    context = {
        'workflow': workflow,
        'systems': list(systems),
        'scripts': list(scripts),
        'workflow_data': json.dumps({
            'nodes': workflow.nodes,
            'edges': workflow.edges,
            'version': workflow.version
        })
    }
    
    return render(request, 'workflows/workflow_designer.html', context)

@require_POST
def save_workflow(request, pk):
    """Save workflow nodes and edges"""
    workflow = get_object_or_404(Workflow, pk=pk)
    data = json.loads(request.body)
    
    # Create a new version if changes were made
    if (workflow.nodes != data.get('nodes') or workflow.edges != data.get('edges')):
        # Store the current state as a version
        workflow.create_new_version()
        
        # Update the workflow with new data
        workflow.nodes = data.get('nodes', [])
        workflow.edges = data.get('edges', [])
        workflow.save()
        
        # Extract system IDs and script IDs from nodes and update M2M relationships
        system_ids = set()
        script_ids = set()
        
        for node in data.get('nodes', []):
            if node.get('type') == 'step':
                node_data = node.get('data', {})
                if node_data.get('system_id'):
                    system_ids.add(node_data.get('system_id'))
                if node_data.get('script_id'):
                    script_ids.add(node_data.get('script_id'))
        
        # Update systems M2M relation if we found system IDs
        if system_ids:
            workflow.systems.set(system_ids)
            
        # Update scripts M2M relation if we found script IDs
        if script_ids:
            workflow.scripts.set(script_ids)
        
        return JsonResponse({
            'success': True, 
            'message': 'Workflow saved successfully',
            'version': workflow.version
        })
    
    return JsonResponse({'success': True, 'message': 'No changes detected'})

def workflow_versions(request, pk):
    """View versions of a workflow"""
    workflow = get_object_or_404(Workflow, pk=pk)
    versions = WorkflowVersion.objects.filter(workflow=workflow)
    
    context = {
        'workflow': workflow,
        'versions': versions
    }
    
    return render(request, 'workflows/workflow_versions.html', context)

def load_workflow_version(request, pk, version):
    """Load a specific version of a workflow"""
    workflow = get_object_or_404(Workflow, pk=pk)
    
    if version == 'current':
        data = {
            'nodes': workflow.nodes,
            'edges': workflow.edges,
            'version': workflow.version
        }
    else:
        version_obj = get_object_or_404(WorkflowVersion, workflow=workflow, version=version)
        data = {
            'nodes': version_obj.nodes,
            'edges': version_obj.edges,
            'version': version_obj.version
        }
    
    return JsonResponse(data)

def restore_workflow_version(request, pk, version):
    """Restore a workflow to a previous version"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
        
    workflow = get_object_or_404(Workflow, pk=pk)
    version_obj = get_object_or_404(WorkflowVersion, workflow=workflow, version=version)
    
    # Create a version of the current state before restoring
    workflow.create_new_version()
    
    # Update workflow with version data
    workflow.nodes = version_obj.nodes
    workflow.edges = version_obj.edges
    workflow.save()
    
    messages.success(request, f'Workflow restored to version {version}')
    return redirect('workflows:designer', pk=workflow.pk)