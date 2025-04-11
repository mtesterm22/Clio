# scripts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Script, ScriptDocument
from .forms import ScriptForm, ScriptDocumentForm

def script_list(request):
    """View to list all scripts"""
    scripts = Script.objects.all()
    
    return render(request, 'scripts/script_list.html', {'scripts': scripts})

def script_detail(request, pk):
    """View details of a script"""
    script = get_object_or_404(Script, pk=pk)
    
    # Get the documents
    documents = script.documents.all()
    
    # Get associated systems
    systems = script.systems.all()
    
    # Get associated workflows
    workflows = script.workflows.all()
    
    context = {
        'script': script,
        'documents': documents,
        'systems': systems,
        'workflows': workflows,
    }
    
    return render(request, 'scripts/script_detail.html', context)

def script_create(request):
    """Create a new script"""
    if request.method == 'POST':
        form = ScriptForm(request.POST)
        if form.is_valid():
            script = form.save()
            messages.success(request, f'Script "{script.name}" was created successfully.')
            return redirect('scripts:detail', pk=script.pk)
    else:
        form = ScriptForm()
    
    return render(request, 'scripts/script_form.html', {'form': form, 'title': 'Create Script'})

def script_update(request, pk):
    """Update an existing script"""
    script = get_object_or_404(Script, pk=pk)
    
    if request.method == 'POST':
        form = ScriptForm(request.POST, instance=script)
        if form.is_valid():
            form.save()
            messages.success(request, f'Script "{script.name}" was updated successfully.')
            return redirect('scripts:detail', pk=script.pk)
    else:
        form = ScriptForm(instance=script)
    
    return render(request, 'scripts/script_form.html', {'form': form, 'script': script, 'title': 'Update Script'})

def script_delete(request, pk):
    """Delete a script"""
    script = get_object_or_404(Script, pk=pk)
    
    if request.method == 'POST':
        script_name = script.name
        script.delete()
        messages.success(request, f'Script "{script_name}" was deleted successfully.')
        return redirect('scripts:list')
    
    return render(request, 'scripts/script_confirm_delete.html', {'script': script})