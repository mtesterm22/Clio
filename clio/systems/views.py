# systems/views.py

import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models, transaction, connection
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST, require_http_methods
from .models import (
    System, SystemRelationship, SystemDocument, SystemNote,
    SystemCategory, SystemStatus, SystemAdministrator, DisasterRecoveryStep
)
from .forms import (
    SystemForm, SystemRelationshipForm, SystemDocumentForm, SystemNoteForm,
    SystemAdministratorForm, SystemCategoryForm, SystemStatusForm  , DisasterRecoveryStepForm
)
from scripts.models import Script, ScriptSystemRelationship

@login_required
def system_list(request):
    """View to list all systems with sorting and filtering"""
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    sso_filter = request.GET.get('sso_system')
    hosting_filter = request.GET.get('hosting_system')
    vendor_filter = request.GET.get('vendor')
    search_query = request.GET.get('search')
    
    # Pagination parameters
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 25)
    
    # Sorting parameters
    sort_by = request.GET.get('sort', 'name')  # Default sort by name
    sort_direction = request.GET.get('direction', 'asc')  # Default ascending
    
    # Start with all systems
    systems = System.objects.all().select_related('category', 'status', 'sso_system', 'hosting_system')
    
    # Apply search filter if provided
    if search_query:
        systems = systems.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(vendor__icontains=search_query) |
            Q(operating_system__icontains=search_query) |
            Q(contact_information__icontains=search_query) |
            Q(support_information__icontains=search_query)
        )
    
    # Apply filters if provided
    if status_filter:
        systems = systems.filter(status_id=status_filter)
    
    if category_filter:
        systems = systems.filter(category_id=category_filter)
    
    # Filter by vendor
    if vendor_filter:
        systems = systems.filter(vendor=vendor_filter)
    
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
    
    # Apply primary and secondary sorting
    order_fields = []
    
    # Primary sort
    if sort_by in ['name', 'vendor', 'updated_at']:
        # These fields are directly on the model and can be sorted with standard methods
        if sort_direction == 'asc':
            order_fields.append(sort_by)
        else:
            order_fields.append(f'-{sort_by}')
    elif sort_by == 'category':
        # For category, we need to use annotate to sort by the related field name
        systems = systems.annotate(
            category_name=models.F('category__name')
        )
        if sort_direction == 'asc':
            order_fields.append('category_name')
        else:
            order_fields.append('-category_name')
    elif sort_by == 'status':
        # For status, we need to use annotate to sort by the related field name
        systems = systems.annotate(
            status_name=models.F('status__name')
        )
        if sort_direction == 'asc':
            order_fields.append('status_name')
        else:
            order_fields.append('-status_name')
    
    # Always add name as a secondary sort key if it's not the primary
    if sort_by != 'name':
        order_fields.append('name')
    
    # Apply the ordering
    if order_fields:
        systems = systems.order_by(*order_fields)
    
    # Get all available categories, statuses, and SSO systems for filters
    all_categories = SystemCategory.objects.all().order_by('order', 'name')
    all_statuses = SystemStatus.objects.all().order_by('order', 'name')
    sso_systems = System.objects.filter(sso_dependent_systems__isnull=False).distinct().order_by('name')
    hosting_systems = System.objects.filter(category__slug='server').order_by('name')
    
    # Get all unique vendors for filtering
    all_vendors = System.objects.exclude(vendor='').values_list('vendor', flat=True).distinct().order_by('vendor')
    
    # Paginate the results
    paginator = Paginator(systems, per_page)
    try:
        systems = paginator.page(page)
    except PageNotAnInteger:
        systems = paginator.page(1)
    except EmptyPage:
        systems = paginator.page(paginator.num_pages)
    
    context = {
        'systems': systems,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'sso_filter': sso_filter,
        'hosting_filter': hosting_filter,
        'vendor_filter': vendor_filter,
        'all_categories': all_categories,
        'all_statuses': all_statuses,
        'all_vendors': all_vendors,
        'sso_systems': sso_systems,
        'hosting_systems': hosting_systems,
        'paginator': paginator,
        'page_obj': systems,
        'per_page': per_page,
    }
    
    return render(request, 'systems/system_list.html', context)

# API endpoint for getting system details
@login_required
def get_system_details(request, pk):
    """API endpoint to get system details for editing"""
    system = get_object_or_404(System, pk=pk)
    
    data = {
        'id': system.id,
        'name': system.name,
        'category': {
            'id': system.category.id,
            'name': system.category.name
        },
        'status': {
            'id': system.status.id,
            'name': system.status.name
        },
        'vendor': system.vendor
    }
    
    return JsonResponse(data)

# API endpoint for quick-updating system details
@login_required
@require_POST
def quick_update_system(request, pk):
    """API endpoint to quickly update system details"""
    system = get_object_or_404(System, pk=pk)
    
    # Update basic fields
    name = request.POST.get('name')
    category_id = request.POST.get('category')
    status_id = request.POST.get('status')
    vendor = request.POST.get('vendor')
    
    # Validate required fields
    if not name or not category_id or not status_id:
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    # Get category and status objects
    category = get_object_or_404(SystemCategory, pk=category_id)
    status = get_object_or_404(SystemStatus, pk=status_id)
    
    # Update system
    system.name = name
    system.category = category
    system.status = status
    system.vendor = vendor
    system.save()
    
    return JsonResponse({'success': True, 'message': 'System updated successfully'})

@login_required
def system_detail(request, pk):
    """View details of a system"""
    system = get_object_or_404(System, pk=pk)
    
    # Get the documents
    documents = system.documents.all()
    
    # Get related systems with proper select_related for category and status
    dependencies = [rel.source_system for rel in system.incoming_relationships.filter(relationship_type='depends_on').select_related('source_system__category', 'source_system__status')]
    dependents = [rel.target_system for rel in system.outgoing_relationships.filter(relationship_type='depends_on').select_related('target_system__category', 'target_system__status')]
    
    # Get systems that use this as SSO
    sso_dependents = system.sso_dependent_systems.all().select_related('category', 'status')
    
    # Get systems hosted on this system
    hosted_systems = system.hosted_systems.all().select_related('category', 'status')
    
    # Get workflows that use this system
    workflows = system.workflows.all() if hasattr(system, 'workflows') else []
    
    # Get scripts associated with this system
    scripts = system.related_scripts.all()
    
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
    
    # Get all systems for relationship management - sorted by name
    all_systems = System.objects.all().order_by('name')
    
    # Get all users for admin management
    all_users = User.objects.all().order_by('first_name', 'last_name')
    
    # Get relationships for this system
    system_relationships = (
        SystemRelationship.objects.filter(source_system=system) | 
        SystemRelationship.objects.filter(target_system=system)
    ).select_related('source_system', 'target_system', 'source_system__category', 'target_system__category')
    
    # Format relationships for JSON
    relationships_json = []
    for rel in system_relationships:
        # Track the IDs of systems in existing relationships
        source_id = rel.source_system.id
        target_id = rel.target_system.id
        
        relationships_json.append({
            'id': rel.id,
            'source_system': {
                'id': source_id,
                'name': rel.source_system.name,
                'category': {
                    'slug': rel.source_system.category.slug,
                    'name': rel.source_system.category.name,
                    'color': rel.source_system.category.color,
                    'text_color': rel.source_system.category.text_color
                } if rel.source_system.category else None
            },
            'target_system': {
                'id': target_id,
                'name': rel.target_system.name,
                'category': {
                    'slug': rel.target_system.category.slug,
                    'name': rel.target_system.category.name,
                    'color': rel.target_system.category.color,
                    'text_color': rel.target_system.category.text_color
                } if rel.target_system.category else None
            },
            'relationship_type': rel.relationship_type,
            'description': rel.description
        })
    
    # Format all systems for JSON - sorted by name
    all_systems_json = []
    for sys in all_systems:
        all_systems_json.append({
            'id': sys.id,
            'name': sys.name,
            'category': {
                'slug': sys.category.slug,
                'name': sys.category.name,
                'color': sys.category.color,
                'text_color': sys.category.text_color
            } if sys.category else None
        })
    
    # Create a list of existing relationships to filter out duplicates in the UI
    existing_relationships = []
    for rel in system_relationships:
        existing_relationships.append({
            'source': rel.source_system.id,
            'target': rel.target_system.id,
            'type': rel.relationship_type
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
        'all_systems_json': json.dumps(all_systems_json),
        'existing_relationships_json': json.dumps(existing_relationships)
    }
    
    return render(request, 'systems/system_detail.html', context)

@login_required
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

@login_required
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

# This function is kept but will be removed from the URLs
@login_required
def system_delete(request, pk):
    """Delete a system"""
    system = get_object_or_404(System, pk=pk)
    
    if request.method == 'POST':
        system_name = system.name
        system.delete()
        messages.success(request, f'System "{system_name}" was deleted successfully.')
        return redirect('systems:list')
    
    return render(request, 'systems/system_confirm_delete.html', {'system': system})

def analyze_system_dependencies(system_id):
    """
    Analyze a system and determine all of its dependencies and dependents
    
    Args:
        system_id: The ID of the system to analyze
        
    Returns:
        dict: Analysis results including dependencies, dependents, and impact paths
    """
    try:
        # Get the source system
        source_system = System.objects.get(id=system_id)
        
        # Build a complete dependency graph
        dependency_graph = build_dependency_graph()
        
        # Find all affected systems with impact levels
        affected_systems = find_affected_systems(dependency_graph, source_system.id)
        
        # Sort affected systems by impact level (depth)
        affected_systems.sort(key=lambda s: (s['impact_level'], s['name']))
        
        return {
            'source_system': {
                'id': source_system.id,
                'name': source_system.name,
                'category': source_system.category.name if source_system.category else None,
                'vendor': source_system.vendor
            },
            'affected_systems': affected_systems
        }
    except System.DoesNotExist:
        return {'error': f'System with ID {system_id} not found'}
    except Exception as e:
        return {'error': str(e)}

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

@login_required
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
            # Properly serialize the category objects
            source_category = {
                'slug': rel.source_system.category.slug,
                'name': rel.source_system.category.name,
                'color': rel.source_system.category.color,
                'text_color': rel.source_system.category.text_color
            } if rel.source_system.category else None
            
            target_category = {
                'slug': rel.target_system.category.slug,
                'name': rel.target_system.category.name,
                'color': rel.target_system.category.color,
                'text_color': rel.target_system.category.text_color
            } if rel.target_system.category else None
            
            updated_relationships_json.append({
                'id': rel.id,
                'source_system': {
                    'id': rel.source_system.id,
                    'name': rel.source_system.name,
                    'category': source_category
                },
                'target_system': {
                    'id': rel.target_system.id,
                    'name': rel.target_system.name,
                    'category': target_category
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

@login_required
def relationship_diagram(request):
    """Show the systems relationship diagram"""
    return render(request, 'systems/relationship_diagram.html')

@login_required
def relationship_data(request):
    """API endpoint to get relationship data for the diagram"""
    systems = []
    links = []
    
    # Get all systems with related category and status
    all_systems = System.objects.all().select_related('category', 'status', 'sso_system', 'hosting_system')
    
    for system in all_systems:
        # Get category and status information
        category = {
            'slug': system.category.slug,
            'name': system.category.name,
            'color': system.category.color,
            'text_color': system.category.text_color,
        } if system.category else {'slug': 'unknown', 'name': 'Unknown', 'color': '#f2f2f2', 'text_color': '#333333'}
        
        status = {
            'slug': system.status.slug,
            'name': system.status.name,
            'color': system.status.color,
            'text_color': system.status.text_color,
            'is_active': system.status.is_active,
        } if system.status else {'slug': 'unknown', 'name': 'Unknown', 'color': '#f2f2f2', 'text_color': '#333333', 'is_active': False}
        
        # Get SSO system data if present
        sso_system = None
        if system.sso_system:
            sso_system = {
                'id': system.sso_system.id,
                'name': system.sso_system.name
            }
        
        # Get hosting system data if present
        hosting_system = None
        if system.hosting_system:
            hosting_system = {
                'id': system.hosting_system.id,
                'name': system.hosting_system.name
            }
        
        systems.append({
            'id': system.id,
            'name': system.name,
            'category': category,
            'status': status,
            'vendor': system.vendor,
            'sso_system': sso_system,
            'hosting_system': hosting_system,
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

@login_required
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

@login_required
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




@login_required
def save_recovery_step(request, system_pk):
    """Save a disaster recovery step"""
    system = get_object_or_404(System, pk=system_pk)
    
    if request.method == 'POST':
        step_id = request.POST.get('step_id')
        
        if step_id:
            # Update existing step
            step = get_object_or_404(DisasterRecoveryStep, pk=step_id, system=system)
            form = DisasterRecoveryStepForm(request.POST, instance=step)
        else:
            # Create new step
            form = DisasterRecoveryStepForm(request.POST)
        
        if form.is_valid():
            step = form.save(commit=False)
            step.system = system
            
            if not step_id:
                # For new steps, set order to the next available
                next_order = DisasterRecoveryStep.objects.filter(system=system).count() + 1
                step.order = next_order
            
            if request.user.is_authenticated:
                step.created_by = request.user
                
            step.save()
            messages.success(request, 'Recovery step saved successfully.')
        else:
            messages.error(request, 'Error saving recovery step: ' + str(form.errors))
    
    return redirect('systems:disaster_analysis', pk=system_pk)

@login_required
def get_recovery_step(request, step_id):
    """API endpoint to get recovery step details"""
    step = get_object_or_404(DisasterRecoveryStep, pk=step_id)
    
    data = {
        'id': step.id,
        'title': step.title,
        'description': step.description,
        'responsible_team': step.responsible_team,
        'estimated_time': step.estimated_time,
        'order': step.order
    }
    
    return JsonResponse(data)

@login_required
def delete_recovery_step(request, system_pk, step_id):
    """Delete a recovery step"""
    system = get_object_or_404(System, pk=system_pk)
    step = get_object_or_404(DisasterRecoveryStep, pk=step_id, system=system)
    
    if request.method == 'POST':
        # Get the order of the deleted step
        deleted_order = step.order
        
        # Delete the step
        step.delete()
        
        # Reorder remaining steps
        steps_to_update = DisasterRecoveryStep.objects.filter(
            system=system, 
            order__gt=deleted_order
        )
        
        # Shift orders down by 1
        for step in steps_to_update:
            step.order -= 1
            step.save()
        
        messages.success(request, 'Recovery step deleted successfully.')
    
    return redirect('systems:disaster_analysis', pk=system_pk)

@login_required
@require_POST
def move_recovery_step(request, system_pk):
    """Move a recovery step up or down in order using raw SQL to avoid constraint issues"""
    try:
        data = json.loads(request.body)
        step_id = data.get('step_id')
        direction = data.get('direction')
        
        if not step_id or direction not in ['up', 'down']:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)
        
        system = get_object_or_404(System, pk=system_pk)
        step = get_object_or_404(DisasterRecoveryStep, pk=step_id, system=system)
        current_order = step.order
        
        # Using raw SQL with a single transaction to avoid constraint violations
        with transaction.atomic():
            with connection.cursor() as cursor:
                if direction == 'up' and current_order > 1:
                    # Find the step above
                    cursor.execute(
                        "SELECT id FROM systems_disasterrecoverystep WHERE system_id = %s AND `order` = %s",
                        [system.id, current_order - 1]
                    )
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("No step found above this one")
                    
                    other_step_id = result[0]
                    
                    # Use a temporary high order number to avoid constraint issues
                    cursor.execute(
                        "UPDATE systems_disasterrecoverystep SET `order` = %s WHERE id = %s",
                        [1000 + current_order, step.id]
                    )
                    
                    # Move the other step down
                    cursor.execute(
                        "UPDATE systems_disasterrecoverystep SET `order` = %s WHERE id = %s",
                        [current_order, other_step_id]
                    )
                    
                    # Move the current step to its final position
                    cursor.execute(
                        "UPDATE systems_disasterrecoverystep SET `order` = %s WHERE id = %s",
                        [current_order - 1, step.id]
                    )
                    
                elif direction == 'down':
                    # Find the step below
                    cursor.execute(
                        "SELECT id FROM systems_disasterrecoverystep WHERE system_id = %s AND `order` = %s",
                        [system.id, current_order + 1]
                    )
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("No step found below this one")
                    
                    other_step_id = result[0]
                    
                    # Use a temporary high order number to avoid constraint issues
                    cursor.execute(
                        "UPDATE systems_disasterrecoverystep SET `order` = %s WHERE id = %s",
                        [1000 + current_order, step.id]
                    )
                    
                    # Move the other step up
                    cursor.execute(
                        "UPDATE systems_disasterrecoverystep SET `order` = %s WHERE id = %s",
                        [current_order, other_step_id]
                    )
                    
                    # Move the current step to its final position
                    cursor.execute(
                        "UPDATE systems_disasterrecoverystep SET `order` = %s WHERE id = %s",
                        [current_order + 1, step.id]
                    )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def build_dependency_graph():
    """
    Build a graph representation of all system dependencies
    
    Returns:
        dict: A graph where keys are system IDs and values are dicts with 
              system information and dependency relationships
    """
    # Start with an empty graph
    graph = {}
    
    # Get all systems and their relationships
    systems = System.objects.all().select_related('category', 'status')
    relationships = SystemRelationship.objects.filter(relationship_type='depends_on')
    
    # Add all systems to the graph
    for system in systems:
        graph[system.id] = {
            'id': system.id,
            'name': system.name,
            'category': {
                'id': system.category.id,
                'name': system.category.name,
                'slug': system.category.slug
            } if system.category else None,
            'status': {
                'id': system.status.id,
                'name': system.status.name,
                'slug': system.status.slug
            } if system.status else None,
            'vendor': system.vendor,
            'depends_on': [],  # Systems this system depends on
            'dependents': []   # Systems that depend on this system
        }
    
    # Add dependency relationships to the graph
    for rel in relationships:
        source_id = rel.source_system_id
        target_id = rel.target_system_id
        
        # Add source as a dependency of target (target depends on source)
        if target_id in graph:
            graph[target_id]['depends_on'].append(source_id)
        
        # Add target as a dependent of source
        if source_id in graph:
            graph[source_id]['dependents'].append(target_id)
    
    return graph

def find_affected_systems(graph, source_id):
    """
    Find all systems affected by an outage of the source system
    
    Args:
        graph: The dependency graph
        source_id: The ID of the system experiencing an outage
        
    Returns:
        list: List of affected systems with their impact levels
    """
    # Track affected systems
    affected = {}
    
    # Helper function to find all systems that depend on a given system
    def find_dependents(system_id, current_path=None, impact_level=1):
        if current_path is None:
            current_path = [system_id]
        
        # Get all direct dependents
        dependents = graph.get(system_id, {}).get('dependents', [])
        
        for dependent_id in dependents:
            # Skip if this would create a loop
            if dependent_id in current_path:
                continue
                
            # Check if the dependent is already affected with a shorter path
            if dependent_id in affected and affected[dependent_id]['impact_level'] <= impact_level:
                continue
                
            # Add the dependent as an affected system
            affected[dependent_id] = {
                'id': dependent_id,
                'name': graph[dependent_id]['name'],
                'category': graph[dependent_id]['category'],
                'vendor': graph[dependent_id]['vendor'],
                'impact_level': impact_level,
                'impact_path': current_path + [dependent_id]
            }
            
            # Recursively find systems that depend on this dependent
            find_dependents(dependent_id, current_path + [dependent_id], impact_level + 1)
    
    # Start the recursive search
    find_dependents(source_id)
    
    # Convert to a list
    return list(affected.values())

def system_disaster_analysis(request, pk):
    """View for the system disaster impact analysis"""
    system = get_object_or_404(System, pk=pk)
    
    # Get the dependencies and dependents
    dependencies = [rel.source_system for rel in system.incoming_relationships.filter(relationship_type='depends_on').select_related('source_system__category', 'source_system__status')]
    dependents = [rel.target_system for rel in system.outgoing_relationships.filter(relationship_type='depends_on').select_related('target_system__category', 'target_system__status')]
    
    # Get systems that use this as SSO
    sso_dependents = system.sso_dependent_systems.all().select_related('category', 'status')
    
    # Get systems hosted on this system
    hosted_systems = system.hosted_systems.all().select_related('category', 'status')
    
    # Get administrators for this system
    administrators = system.administrators.all().select_related('user').order_by('-is_primary', 'user__first_name')
    
    # Get recovery steps for this system
    recovery_steps = system.recovery_steps.all().order_by('order')
    
    context = {
        'system': system,
        'dependencies': dependencies,
        'dependents': dependents,
        'sso_dependents': sso_dependents,
        'hosted_systems': hosted_systems,
        'administrators': administrators,
        'recovery_steps': recovery_steps,
    }
    
    return render(request, 'systems/system_disaster_analysis.html', context)

# For API access to get affected systems
@login_required
def get_affected_systems(request, pk):
    """API endpoint to get systems affected by an outage of the specified system"""
    # Analyze dependencies
    analysis = analyze_system_dependencies(pk)
    
    # Return as JSON
    return JsonResponse(analysis)