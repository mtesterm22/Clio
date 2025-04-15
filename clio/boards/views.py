# boards/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import json

from .models import Board, Card, CardComment, CardDocument
from .forms import CardForm, CardCommentForm, CardDocumentForm, BoardForm
from systems.models import System
from workflows.models import Workflow
from scripts.models import Script

@login_required
def board_list(request):
    """View to list all boards"""
    boards = Board.objects.all()
    
    context = {
        'boards': boards,
    }
    
    return render(request, 'boards/board_list.html', context)


@login_required
def board_detail(request, pk):
    """View a specific board"""
    board = get_object_or_404(Board, pk=pk)
    
    # Filter cards based on board context if applicable
    if board.systems.exists() or board.workflows.exists() or board.scripts.exists():
        cards = Card.objects.filter(
            Q(systems__in=board.systems.all()) |
            Q(workflows__in=board.workflows.all()) |
            Q(scripts__in=board.scripts.all())
        ).distinct()
    else:
        # Board has no context filtering, show all cards
        cards = Card.objects.all()
    
    # Get systems, workflows, and scripts for filters
    systems = System.objects.all()
    workflows = Workflow.objects.all()
    scripts = Script.objects.all()
    
    context = {
        'board': board,
        'cards': cards,
        'systems': systems,
        'workflows': workflows,
        'scripts': scripts,
        'card_types': Card.TYPE_CHOICES,
        'card_statuses': Card.STATUS_CHOICES,
    }
    
    return render(request, 'boards/board_detail.html', context)


@login_required
def board_create(request):
    """Create a new board"""
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.created_by = request.user
            board.save()
            # Handle many-to-many relationships
            form.save_m2m()
            
            messages.success(request, f'Board "{board.name}" was created successfully.')
            return redirect('boards:detail', pk=board.pk)
    else:
        form = BoardForm()
    
    context = {
        'form': form,
        'title': 'Create Board',
    }
    
    return render(request, 'boards/board_form.html', context)


@login_required
def card_list(request):
    """View to list all cards with filtering"""
    # Get filter parameters
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    system_filter = request.GET.get('system')
    workflow_filter = request.GET.get('workflow')
    script_filter = request.GET.get('script')
    assigned_filter = request.GET.get('assigned_to')
    checkout_filter = request.GET.get('checked_out')
    search_query = request.GET.get('search')
    
    # Start with all cards
    cards = Card.objects.all()
    
    # Apply filters
    if status_filter:
        cards = cards.filter(status=status_filter)
    
    if type_filter:
        cards = cards.filter(type=type_filter)
    
    if system_filter:
        cards = cards.filter(systems__id=system_filter)
    
    if workflow_filter:
        cards = cards.filter(workflows__id=workflow_filter)
    
    if script_filter:
        cards = cards.filter(scripts__id=script_filter)
    
    # Assignment filter
    if assigned_filter:
        if assigned_filter == 'me':
            cards = cards.filter(assigned_to=request.user)
        elif assigned_filter == 'unassigned':
            cards = cards.filter(assigned_to__isnull=True)
        else:
            cards = cards.filter(assigned_to_id=assigned_filter)
    
    # Checkout filter
    if checkout_filter:
        if checkout_filter == 'checked_out':
            cards = cards.filter(checked_out=True)
        elif checkout_filter == 'not_checked_out':
            cards = cards.filter(checked_out=False)
        elif checkout_filter == 'checked_out_by_me':
            cards = cards.filter(checked_out=True, assigned_to=request.user)
    
    if search_query:
        cards = cards.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Get filter options
    systems = System.objects.all()
    workflows = Workflow.objects.all()
    scripts = Script.objects.all()
    users = User.objects.all()
    
    context = {
        'cards': cards,
        'systems': systems,
        'workflows': workflows,
        'scripts': scripts,
        'users': users,
        'card_types': Card.TYPE_CHOICES,
        'card_statuses': Card.STATUS_CHOICES,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'system_filter': system_filter,
        'workflow_filter': workflow_filter,
        'script_filter': script_filter,
        'assigned_filter': assigned_filter,
        'checkout_filter': checkout_filter,
        'search_query': search_query,
    }
    
    return render(request, 'boards/card_list.html', context)


@login_required
def card_detail(request, pk):
    """View details of a card"""
    card = get_object_or_404(Card, pk=pk)
    
    # Get comments
    comments = card.comments.all()
    
    # Get documents
    documents = card.documents.all()
    
    # Handle new comment form
    if request.method == 'POST' and 'comment_form' in request.POST:
        comment_form = CardCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.card = card
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('boards:card_detail', pk=card.pk)
    else:
        comment_form = CardCommentForm()
    
    # Handle document upload form
    if request.method == 'POST' and 'document_form' in request.POST:
        document_form = CardDocumentForm(request.POST, request.FILES)
        if document_form.is_valid():
            document = document_form.save(commit=False)
            document.card = card
            document.uploaded_by = request.user
            document.save()
            messages.success(request, f'Document "{document.name}" was uploaded successfully.')
            return redirect('boards:card_detail', pk=card.pk)
    else:
        document_form = CardDocumentForm()
    
    context = {
        'card': card,
        'comments': comments,
        'documents': documents,
        'comment_form': comment_form,
        'document_form': document_form,
    }
    
    return render(request, 'boards/card_detail.html', context)


@login_required
def card_create(request, board_pk=None):
    """Create a new card"""
    board = None
    if board_pk:
        board = get_object_or_404(Board, pk=board_pk)
    
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.created_by = request.user
            
            # Set initial position if board is specified
            if board:
                # Generate a position that doesn't overlap with existing cards
                # This is a simple implementation - you might want a more sophisticated positioning algorithm
                existing_cards = Card.objects.all()
                if existing_cards.exists():
                    max_x = existing_cards.order_by('-position_x').first().position_x
                    max_y = existing_cards.order_by('-position_y').first().position_y
                    card.position_x = max_x + 50 if max_x > 0 else 50
                    card.position_y = max_y + 50 if max_y > 0 else 50
                else:
                    card.position_x = 50
                    card.position_y = 50
            
            card.save()
            
            # Handle many-to-many relationships
            form.save_m2m()
            
            messages.success(request, f'Card "{card.title}" was created successfully.')
            if board:
                return redirect('boards:detail', pk=board.pk)
            else:
                return redirect('boards:card_detail', pk=card.pk)
    else:
        # Pre-populate form with board-related systems, workflows, scripts if board is specified
        initial = {}
        if board:
            initial = {
                'systems': board.systems.all(),
                'workflows': board.workflows.all(),
                'scripts': board.scripts.all(),
            }
        form = CardForm(initial=initial)
    
    context = {
        'form': form,
        'board': board,
        'title': 'Create Card',
    }
    
    return render(request, 'boards/card_form.html', context)


@login_required
def card_update(request, pk):
    """Update an existing card"""
    card = get_object_or_404(Card, pk=pk)
    
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, f'Card "{card.title}" was updated successfully.')
            return redirect('boards:card_detail', pk=card.pk)
    else:
        form = CardForm(instance=card)
    
    context = {
        'form': form,
        'card': card,
        'title': 'Update Card',
    }
    
    return render(request, 'boards/card_form.html', context)


@login_required
def card_checkout(request, pk):
    """Check out or check in a card"""
    card = get_object_or_404(Card, pk=pk)
    
    # Toggle checked_out status
    if card.checked_out and card.assigned_to == request.user:
        # User is checking in their own card
        card.checked_out = False
        card.save()
        messages.success(request, f'Card "{card.title}" has been checked in.')
    elif card.checked_out:
        # Card is already checked out by someone else
        messages.error(request, f'Card "{card.title}" is already checked out by {card.assigned_to}.')
    else:
        # Card is available for checkout
        card.checked_out = True
        card.assigned_to = request.user
        card.save()
        messages.success(request, f'Card "{card.title}" has been checked out to you.')
    
    # Redirect back to the card detail view
    return redirect('boards:card_detail', pk=card.pk)


@login_required
@require_POST
def save_card_position(request):
    """API endpoint to save card position changes"""
    try:
        data = json.loads(request.body)
        card_id = data.get('id')
        position_x = data.get('x')
        position_y = data.get('y')
        
        if not card_id or position_x is None or position_y is None:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        card = get_object_or_404(Card, pk=card_id)
        card.position_x = position_x
        card.position_y = position_y
        card.save(update_fields=['position_x', 'position_y'])
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def upload_document(request, card_pk):
    """Upload a document to a card"""
    card = get_object_or_404(Card, pk=card_pk)
    
    if request.method == 'POST':
        form = CardDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.card = card
            document.uploaded_by = request.user
            document.save()
            messages.success(request, f'Document "{document.name}" was uploaded successfully.')
            return redirect('boards:card_detail', pk=card.pk)
    else:
        form = CardDocumentForm()
    
    context = {
        'form': form,
        'card': card,
        'title': 'Upload Document',
    }
    
    return render(request, 'boards/document_form.html', context)