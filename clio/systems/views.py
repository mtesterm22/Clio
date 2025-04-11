# systems/views.py

import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Add this import
from django.db import models
from .models import (
    System, SystemRelationship, SystemDocument, SystemNote,
    SystemCategory, SystemStatus, SystemAdministrator
)
from .forms import (
    SystemForm, SystemRelationshipForm, SystemDocumentForm, SystemNoteForm,
    SystemAdministratorForm, SystemCategoryForm, SystemStatusForm  
)

# Continued from previous system_list view
def system_list(request):
    """View to list all systems with sorting and filtering"""
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    sso_filter = request.GET.get('sso_system')
    hosting_filter = request.GET.get('hosting_system')
    sort_by = request.GET.get('sort', 'name')  # Default sort by name
    sort_direction = request.GET.get('direction', 'asc')  # Default ascending
    
    # Start with all systems
    systems = System.objects.all().select_related('category', 'status', 'sso_system', 'hosting_system')
    
    # Apply filters if provided
    if status_filter:
        systems = systems.filter(status_id=status_filter)
    
    if category_filter:
        systems = systems.filter(category_id=category_filter)
    
    # Filter by SSO system
    if sso_filter:
        if sso_filter == 'none':
            systems = systems.filter(sso_system__isnull=True)
        else:
            systems = systems.filter(sso_system_id=sso_filter)
    
    # Filter by hosting system
    if hosting_filter:
        if hosting_filter == 'none':
            systems = systems.filter(hosting_system__isnull=True)
        else:
            systems = systems.filter(hosting_system_id=hosting_filter)
    
    # Apply sorting with nulls last
    if sort_by in ['name', 'vendor']:
        if sort_by == 'vendor':
            # When sorting by vendor, put nulls last
            if sort_direction == 'asc':
                systems = systems.order_by(models.F(sort_by).asc(nulls_last=True))
            else:
                systems = systems.order_by(models.F(sort_by).desc(nulls_last=True))
        else:
            # For name or other fields, standard ordering
            order_prefix = '' if sort_direction == 'asc' else '-'
            systems = systems.order_by(f'{order_prefix}{sort_by}')
    
    # Get all available categories, statuses, and SSO systems for filters
    all_categories = SystemCategory.objects.all().order_by('order', 'name')
    all_statuses = SystemStatus.objects.all().order_by('order', 'name')
    sso_systems = System.objects.filter(sso_dependent_systems__isnull=False).distinct().order_by('name')
    hosting_systems = System.objects.filter(category__slug='server').order_by('name')
    
    context = {
        'systems': systems,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'sso_filter': sso_filter,
        'hosting_filter': hosting_filter,
        'all_categories': all_categories,
        'all_statuses': all_statuses,
        'sso_systems': sso_systems,
        'hosting_systems': hosting_systems,
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
    
    # Get systems that use this as SSO
    sso_dependents = system.sso_dependent_systems.all()
    
    # Get systems hosted on this system
    hosted_systems = system.hosted_systems.all()
    
    # Get workflows that use this system
    workflows = system.workflows.all() if hasattr(system, 'workflows') else []
    
    # Get scripts associated with this system
    scripts = system.scripts.all() if hasattr(system, 'scripts') else []
    
    # Get notes for this system
    notes = system.notes.all()
    
    # Get administrators for this system
    administrators = system.administrators.all().select_related('user').order_by('-is_primary', 'user__first_name')
    
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
    
    # Get all users for admin management
    all_users = User.objects.all().order_by('first_name', 'last_name')
    
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
                'category': rel.source_system.category.slug
            },
            'target_system': {
                'id': rel.target_system.id,
                'name': rel.target_system.name,
                'category': rel.target_system.category.slug
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
            'category': sys.category.slug
        })
    
    context = {
        'system': system,
        'documents': documents,
        'dependencies': dependencies,
        'dependents': dependents,
        'sso_dependents': sso_dependents,
        'hosted_systems': hosted_systems,
        'workflows': workflows,
        'scripts': scripts,
        'notes': notes,
        'administrators': administrators,
        'note_form': note_form,
        'all_systems': all_systems,
        'all_users': all_users,
        'relationships_json': json.dumps(relationships_json),
        'all_systems_json': json.dumps(all_systems_json)
    }
    
    return render(request, 'systems/system_detail.html', context)

def system_create(request):
    """Create a new system"""
    if request.method == 'POST':
        form = SystemForm(request.POST)
        if form.is_valid():
            system = form.save()
            messages.success(request, f'System "{system.name}" was created successfully.')
            return redirect('systems:detail', pk=system.pk)
    else:
        # Set default category and status
        try:
            default_category = SystemCategory.objects.get(slug='core')
            default_status = SystemStatus.objects.get(slug='active')
            form = SystemForm(initial={'category': default_category, 'status': default_status})
        except (SystemCategory.DoesNotExist, SystemStatus.DoesNotExist):
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

@login_required
def add_system_administrator(request, system_pk):
    """Add or update an administrator for a system"""
    system = get_object_or_404(System, pk=system_pk)
    
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        
        # Determine if adding new or updating existing
        if admin_id:
            # Updating existing
            admin = get_object_or_404(SystemAdministrator, pk=admin_id, system=system)
            form = SystemAdministratorForm(request.POST, instance=admin)
        else:
            # Adding new
            form = SystemAdministratorForm(request.POST)
        
        if form.is_valid():
            admin = form.save(commit=False)
            admin.system = system
            admin.save()
            
            messages.success(request, 'Administrator updated successfully.')
        else:
            messages.error(request, 'Error updating administrator: ' + str(form.errors))
    
    return redirect('systems:detail', pk=system_pk)

@login_required
def remove_system_administrator(request, system_pk):
    """Remove an administrator from a system"""
    system = get_object_or_404(System, pk=system_pk)
    
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        if admin_id:
            try:
                admin = SystemAdministrator.objects.get(pk=admin_id, system=system)
                admin.delete()
                messages.success(request, 'Administrator removed successfully.')
            except SystemAdministrator.DoesNotExist:
                messages.error(request, 'Administrator not found.')
    
    return redirect('systems:detail', pk=system_pk)

@login_required
def get_administrator_details(request, admin_pk):
    """API endpoint to get administrator details for editing"""
    admin = get_object_or_404(SystemAdministrator, pk=admin_pk)
    
    data = {
        'id': admin.id,
        'user_id': admin.user.id,
        'is_primary': admin.is_primary,
        'notes': admin.notes
    }
    
    return JsonResponse(data)

# @login_required  # Commented out for testing, but should be uncommented in production
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
        
        # First delete all relationships to avoid unique constraint violations
        # This ensures we don't run into issues with partially updated relationships
        current_relationships.delete()
        
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
            try:
                source_system = System.objects.get(pk=source_id)
                target_system = System.objects.get(pk=target_id)
            except System.DoesNotExist:
                continue
            
            # Create new relationship
            relationship = SystemRelationship.objects.create(
                source_system=source_system,
                target_system=target_system,
                relationship_type=rel_type,
                description=description
            )
            relationship_ids_to_keep.append(relationship.id)
        
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
    all_systems = System.objects.all().select_related('category', 'status')  # Add select_related for efficiency
    
    for system in all_systems:
        # Safely get category and status values
        category_slug = system.category.slug if system.category else "unknown"
        status_slug = system.status.slug if system.status else "unknown"
        
        systems.append({
            'id': system.id,
            'name': system.name,
            'category': category_slug,
            'status': status_slug,
            'type': category_slug,  # Using category_slug for type
        })
    
    # Get all relationships
    relationships = SystemRelationship.objects.all().select_related('source_system', 'target_system')
    
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
# Category and Status management views

@login_required
def category_list(request):
    """List and manage system categories"""
    categories = SystemCategory.objects.all().order_by('order', 'name')
    
    context = {
        'categories': categories,
        'title': 'System Categories'
    }
    
    return render(request, 'systems/category_list.html', context)

@login_required
def category_create(request):
    """Create a new system category"""
    if request.method == 'POST':
        form = SystemCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" was created successfully.')
            return redirect('systems:category_list')
    else:
        form = SystemCategoryForm()
    
    context = {
        'form': form,
        'title': 'Create Category'
    }
    
    return render(request, 'systems/category_form.html', context)

@login_required
def category_update(request, pk):
    """Update an existing system category"""
    category = get_object_or_404(SystemCategory, pk=pk)
    
    if request.method == 'POST':
        form = SystemCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" was updated successfully.')
            return redirect('systems:category_list')
    else:
        form = SystemCategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': 'Update Category'
    }
    
    return render(request, 'systems/category_form.html', context)

@login_required
def category_delete(request, pk):
    """Delete a system category"""
    category = get_object_or_404(SystemCategory, pk=pk)
    
    # Check if any systems are using this category
    if System.objects.filter(category=category).exists():
        messages.error(request, f'Cannot delete category "{category.name}" because it is used by one or more systems.')
        return redirect('systems:category_list')
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" was deleted successfully.')
        return redirect('systems:category_list')
    
    context = {
        'category': category,
        'title': 'Delete Category'
    }
    
    return render(request, 'systems/category_confirm_delete.html', context)

@login_required
def status_list(request):
    """List and manage system statuses"""
    statuses = SystemStatus.objects.all().order_by('order', 'name')
    
    context = {
        'statuses': statuses,
        'title': 'System Statuses'
    }
    
    return render(request, 'systems/status_list.html', context)

@login_required
def status_create(request):
    """Create a new system status"""
    if request.method == 'POST':
        form = SystemStatusForm(request.POST)
        if form.is_valid():
            status = form.save()
            messages.success(request, f'Status "{status.name}" was created successfully.')
            return redirect('systems:status_list')
    else:
        form = SystemStatusForm()
    
    context = {
        'form': form,
        'title': 'Create Status'
    }
    
    return render(request, 'systems/status_form.html', context)

@login_required
def status_update(request, pk):
    """Update an existing system status"""
    status = get_object_or_404(SystemStatus, pk=pk)
    
    if request.method == 'POST':
        form = SystemStatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            messages.success(request, f'Status "{status.name}" was updated successfully.')
            return redirect('systems:status_list')
    else:
        form = SystemStatusForm(instance=status)
    
    context = {
        'form': form,
        'status': status,
        'title': 'Update Status'
    }
    
    return render(request, 'systems/status_form.html', context)

@login_required
def status_delete(request, pk):
    """Delete a system status"""
    status = get_object_or_404(SystemStatus, pk=pk)
    
    # Check if any systems are using this status
    if System.objects.filter(status=status).exists():
        messages.error(request, f'Cannot delete status "{status.name}" because it is used by one or more systems.')
        return redirect('systems:status_list')
    
    if request.method == 'POST':
        status_name = status.name
        status.delete()
        messages.success(request, f'Status "{status_name}" was deleted successfully.')
        return redirect('systems:status_list')
    
    context = {
        'status': status,
        'title': 'Delete Status'
    }
    
    return render(request, 'systems/status_confirm_delete.html', context)


def systems_by_sso(request, sso_id):
    """View systems that use a specific SSO system"""
    sso_system = get_object_or_404(System, pk=sso_id)
    systems = System.objects.filter(sso_system=sso_system).select_related('category', 'status')
    
    context = {
        'sso_system': sso_system,
        'systems': systems,
        'title': f'Systems using {sso_system.name} for SSO'
    }
    
    return render(request, 'systems/systems_by_filter.html', context)


def systems_by_host(request, host_id):
    """View systems hosted on a specific system"""
    host_system = get_object_or_404(System, pk=host_id)
    systems = System.objects.filter(hosting_system=host_system).select_related('category', 'status')
    
    context = {
        'host_system': host_system,
        'systems': systems,
        'title': f'Systems hosted on {host_system.name}'
    }
    
    return render(request, 'systems/systems_by_filter.html', context)