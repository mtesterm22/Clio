# systems/views.py


import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import System, SystemRelationship, SystemDocument, SystemNote
from .forms import SystemForm, SystemRelationshipForm, SystemDocumentForm, SystemNoteForm


def system_list(request):
    """View to list all systems"""
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    
    systems = System.objects.all()
    
    if status_filter:
        systems = systems.filter(status=status_filter)
    
    if category_filter:
        systems = systems.filter(category=category_filter)
    
    context = {
        'systems': systems,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': System.STATUS_CHOICES,
        'category_choices': System.CATEGORY_CHOICES,
    }
    
    return render(request, 'systems/system_list.html', context)


def system_detail(request, pk):
    """View details of a system"""
    system = get_object_or_404(System, pk=pk)
    
    # Get the documents
    documents = system.documents.all()
    
    # Get related systems
    dependencies = system.get_dependencies()
    dependents = system.get_dependents()
    
    # Get workflows that use this system
    workflows = system.workflows.all()
    
    # Get scripts associated with this system
    scripts = system.scripts.all()
    
    # Get notes for this system
    notes = system.notes.all()
    
    # Handle note creation
    if request.method == 'POST':
        note_form = SystemNoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.system = system
            if request.user.is_authenticated:
                note.created_by = request.user
            note.save()
            messages.success(request, 'Note added successfully.')
            return redirect('systems:detail', pk=system.pk)
    else:
        note_form = SystemNoteForm()
    
    # Get all systems for relationship management
    all_systems = System.objects.all()
    
    # Get relationships for this system
    system_relationships = (
        SystemRelationship.objects.filter(source_system=system) | 
        SystemRelationship.objects.filter(target_system=system)
    ).select_related('source_system', 'target_system')
    
    # Format relationships for JSON
    relationships_json = []
    for rel in system_relationships:
        relationships_json.append({
            'id': rel.id,
            'source_system': {
                'id': rel.source_system.id,
                'name': rel.source_system.name,
                'category': rel.source_system.category
            },
            'target_system': {
                'id': rel.target_system.id,
                'name': rel.target_system.name,
                'category': rel.target_system.category
            },
            'relationship_type': rel.relationship_type,
            'description': rel.description
        })
    
    # Format all systems for JSON
    all_systems_json = []
    for sys in all_systems:
        all_systems_json.append({
            'id': sys.id,
            'name': sys.name,
            'category': sys.category
        })
    
    context = {
        'system': system,
        'documents': documents,
        'dependencies': dependencies,
        'dependents': dependents,
        'workflows': workflows,
        'scripts': scripts,
        'notes': notes,
        'note_form': note_form,
        'all_systems': all_systems,
        'relationships_json': json.dumps(relationships_json),
        'all_systems_json': json.dumps(all_systems_json)
    }
    
    return render(request, 'systems/system_detail.html', context)

# @login_required
def save_system_relationships(request, pk):
    """API endpoint to save system relationships"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    system = get_object_or_404(System, pk=pk)
    
    try:
        data = json.loads(request.body)
        relationships_data = data.get('relationships', [])
        
        # Get current relationships
        current_relationships = SystemRelationship.objects.filter(
            source_system=system
        ) | SystemRelationship.objects.filter(
            target_system=system
        )
        
        # Track which relationships to keep
        relationship_ids_to_keep = []
        
        # Create or update relationships
        for rel_data in relationships_data:
            rel_id = rel_data.get('id')
            source_id = rel_data.get('source_system_id')
            target_id = rel_data.get('target_system_id')
            rel_type = rel_data.get('relationship_type')
            description = rel_data.get('description', '')
            
            # Skip if missing required fields
            if not all([source_id, target_id, rel_type]):
                continue
                
            # Get the related systems
            source_system = get_object_or_404(System, pk=source_id)
            target_system = get_object_or_404(System, pk=target_id)
            
            if rel_id:
                # Update existing relationship
                try:
                    relationship = SystemRelationship.objects.get(pk=rel_id)
                    relationship.source_system = source_system
                    relationship.target_system = target_system
                    relationship.relationship_type = rel_type
                    relationship.description = description
                    relationship.save()
                    relationship_ids_to_keep.append(relationship.id)
                except SystemRelationship.DoesNotExist:
                    # If the relationship doesn't exist, create a new one
                    relationship = SystemRelationship.objects.create(
                        source_system=source_system,
                        target_system=target_system,
                        relationship_type=rel_type,
                        description=description
                    )
                    relationship_ids_to_keep.append(relationship.id)
            else:
                # Create new relationship
                relationship = SystemRelationship.objects.create(
                    source_system=source_system,
                    target_system=target_system,
                    relationship_type=rel_type,
                    description=description
                )
                relationship_ids_to_keep.append(relationship.id)
        
        # Delete relationships that weren't in the submitted data
        current_relationships.exclude(id__in=relationship_ids_to_keep).delete()
        
        # Get updated relationships
        updated_relationships = SystemRelationship.objects.filter(
            source_system=system
        ) | SystemRelationship.objects.filter(
            target_system=system
        )
        
        # Format updated relationships for response
        updated_relationships_json = []
        for rel in updated_relationships:
            updated_relationships_json.append({
                'id': rel.id,
                'source_system': {
                    'id': rel.source_system.id,
                    'name': rel.source_system.name,
                    'category': rel.source_system.category
                },
                'target_system': {
                    'id': rel.target_system.id,
                    'name': rel.target_system.name,
                    'category': rel.target_system.category
                },
                'relationship_type': rel.relationship_type,
                'description': rel.description
            })
        
        return JsonResponse({
            'success': True,
            'relationships': updated_relationships_json
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def system_create(request):
    """Create a new system"""
    if request.method == 'POST':
        form = SystemForm(request.POST)
        if form.is_valid():
            system = form.save()
            messages.success(request, f'System "{system.name}" was created successfully.')
            return redirect('systems:detail', pk=system.pk)
    else:
        form = SystemForm()
    
    return render(request, 'systems/system_form.html', {'form': form, 'title': 'Create System'})


def system_update(request, pk):
    """Update an existing system"""
    system = get_object_or_404(System, pk=pk)
    
    if request.method == 'POST':
        form = SystemForm(request.POST, instance=system)
        if form.is_valid():
            form.save()
            messages.success(request, f'System "{system.name}" was updated successfully.')
            return redirect('systems:detail', pk=system.pk)
    else:
        form = SystemForm(instance=system)
    
    return render(request, 'systems/system_form.html', {'form': form, 'system': system, 'title': 'Update System'})


def system_delete(request, pk):
    """Delete a system"""
    system = get_object_or_404(System, pk=pk)
    
    if request.method == 'POST':
        system_name = system.name
        system.delete()
        messages.success(request, f'System "{system_name}" was deleted successfully.')
        return redirect('systems:list')
    
    return render(request, 'systems/system_confirm_delete.html', {'system': system})


def relationship_diagram(request):
    """Show the systems relationship diagram"""
    return render(request, 'systems/relationship_diagram.html')


def relationship_data(request):
    """API endpoint to get relationship data for the diagram"""
    systems = []
    links = []
    
    # Get all systems
    all_systems = System.objects.all()
    
    for system in all_systems:
        systems.append({
            'id': system.id,
            'name': system.name,
            'category': system.category,
            'status': system.status,
            'type': system.category,  # Using category as type for visualization
        })
    
    # Get all relationships
    relationships = SystemRelationship.objects.all()
    
    for rel in relationships:
        links.append({
            'source': rel.source_system.id,
            'target': rel.target_system.id,
            'type': rel.relationship_type,
        })
    
    return JsonResponse({'systems': systems, 'links': links})


@login_required
def delete_system_note(request, system_pk, note_pk):
    """Delete a system note"""
    note = get_object_or_404(SystemNote, pk=note_pk, system__pk=system_pk)
    
    # Check if the user is the creator of the note or a superuser
    if request.user != note.created_by and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this note.')
        return redirect('systems:detail', pk=system_pk)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully.')
        return redirect('systems:detail', pk=system_pk)
    
    return render(request, 'systems/note_confirm_delete.html', {
        'note': note,
        'system': note.system
    })

@login_required
def edit_system_note(request, system_pk, note_pk):
    """Edit a system note"""
    note = get_object_or_404(SystemNote, pk=note_pk, system__pk=system_pk)
    
    # Check if the user is the creator of the note or a superuser
    if request.user != note.created_by and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this note.')
        return redirect('systems:detail', pk=system_pk)
    
    if request.method == 'POST':
        form = SystemNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated successfully.')
            return redirect('systems:detail', pk=system_pk)
    else:
        form = SystemNoteForm(instance=note)
    
    return render(request, 'systems/note_form.html', {
        'form': form,
        'note': note,
        'system': note.system
    })