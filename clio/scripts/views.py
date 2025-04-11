# scripts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Script, ScriptDocument, ScriptSystemRelationship
from .forms import ScriptForm, ScriptDocumentForm, ScriptSystemRelationshipForm

def script_list(request):
    """View to list all scripts with filtering options"""
    scripts = Script.objects.all().select_related('hosted_on')
    
    # Apply filters if provided
    language_filter = request.GET.get('language')
    system_filter = request.GET.get('system')
    host_filter = request.GET.get('host')
    
    if language_filter:
        scripts = scripts.filter(programming_language__icontains=language_filter)
        
    if system_filter:
        scripts = scripts.filter(systems__id=system_filter).distinct()
        
    if host_filter:
        scripts = scripts.filter(
            Q(hosted_on_id=host_filter) | 
            Q(host_location__icontains=host_filter)
        )
    
    # Get unique programming languages for filter dropdown
    languages = Script.objects.values_list('programming_language', flat=True).distinct()
    languages = [lang for lang in languages if lang]  # Remove empty values
    
    # Get unique host systems for filter dropdown
    host_systems = Script.objects.exclude(hosted_on__isnull=True).values_list(
        'hosted_on__id', 'hosted_on__name'
    ).distinct()
    
    context = {
        'scripts': scripts,
        'language_filter': language_filter,
        'system_filter': system_filter,
        'host_filter': host_filter,
        'languages': languages,
        'host_systems': host_systems,
    }
    
    return render(request, 'scripts/script_list.html', context)

def script_detail(request, pk):
    """View details of a script"""
    script = get_object_or_404(Script, pk=pk)
    
    # Get the documents
    documents = script.documents.all()
    
    # Get associated system relationships with details
    system_relationships = script.system_relationships.all().select_related('system')
    
    # Get associated workflows
    workflows = script.workflows.all()
    
    # Handle document upload
    if request.method == 'POST' and 'document_form' in request.POST:
        doc_form = ScriptDocumentForm(request.POST, request.FILES)
        if doc_form.is_valid():
            document = doc_form.save(commit=False)
            document.script = script
            document.save()
            messages.success(request, f'Document "{document.name}" was uploaded successfully.')
            return redirect('scripts:detail', pk=script.pk)
        rel_form = ScriptSystemRelationshipForm()
    # Handle system relationship addition
    elif request.method == 'POST' and 'relationship_form' in request.POST:
        rel_form = ScriptSystemRelationshipForm(request.POST)
        if rel_form.is_valid():
            relationship = rel_form.save(commit=False)
            relationship.script = script
            
            # Check if the relationship already exists
            if not ScriptSystemRelationship.objects.filter(
                script=script, system=relationship.system
            ).exists():
                relationship.save()
                messages.success(
                    request, 
                    f'Relationship with "{relationship.system.name}" added successfully.'
                )
            else:
                messages.error(
                    request, 
                    f'A relationship with "{relationship.system.name}" already exists.'
                )
            return redirect('scripts:detail', pk=script.pk)
        doc_form = ScriptDocumentForm()
    else:
        doc_form = ScriptDocumentForm()
        rel_form = ScriptSystemRelationshipForm()
    
    context = {
        'script': script,
        'documents': documents,
        'system_relationships': system_relationships,
        'workflows': workflows,
        'doc_form': doc_form,
        'rel_form': rel_form,
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

def delete_system_relationship(request, script_pk, relationship_pk):
    """Delete a system relationship"""
    relationship = get_object_or_404(
        ScriptSystemRelationship, 
        pk=relationship_pk, 
        script_id=script_pk
    )
    
    if request.method == 'POST':
        system_name = relationship.system.name
        relationship.delete()
        messages.success(request, f'Relationship with "{system_name}" was removed successfully.')
        return redirect('scripts:detail', pk=script_pk)
    
    return render(request, 'scripts/relationship_confirm_delete.html', {
        'relationship': relationship,
        'script': relationship.script
    })

def update_system_relationship(request, script_pk, relationship_pk):
    """Update a system relationship"""
    relationship = get_object_or_404(
        ScriptSystemRelationship, 
        pk=relationship_pk, 
        script_id=script_pk
    )
    
    if request.method == 'POST':
        form = ScriptSystemRelationshipForm(request.POST, instance=relationship)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                f'Relationship with "{relationship.system.name}" was updated successfully.'
            )
            return redirect('scripts:detail', pk=script_pk)
    else:
        form = ScriptSystemRelationshipForm(instance=relationship)
    
    return render(request, 'scripts/relationship_form.html', {
        'form': form,
        'relationship': relationship,
        'script': relationship.script,
        'title': 'Update System Relationship'
    })