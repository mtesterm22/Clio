# boards/models.py

from django.db import models
from django.contrib.auth.models import User
from systems.models import System
from scripts.models import Script
from workflows.models import Workflow

class Card(models.Model):
    """Model for cards representing issues, ideas, features, etc."""
    
    TYPE_CHOICES = [
        ('issue', 'Issue'),
        ('idea', 'Idea'),
        ('feature', 'Feature'),
        ('refinement', 'Refinement'),
        ('task', 'Task'),
    ]
    
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('in-progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('archived', 'Archived'),
    ]
    
    # Basic information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='issue')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    
    # Position for board view
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    
    # Assignment and checkout
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_cards'
    )
    checked_out = models.BooleanField(default=False)
    
    # Primary relationships
    primary_system = models.ForeignKey(
        System, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='primary_for_cards'
    )
    primary_workflow = models.ForeignKey(
        Workflow, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='primary_for_cards'
    )
    primary_script = models.ForeignKey(
        Script, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='primary_for_cards'
    )
    
    # Related items (many-to-many)
    systems = models.ManyToManyField(System, related_name='related_cards', blank=True)
    workflows = models.ManyToManyField(Workflow, related_name='related_cards', blank=True)
    scripts = models.ManyToManyField(Script, related_name='related_cards', blank=True)
    
    # Metadata
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_cards'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"
    
    class Meta:
        ordering = ['-updated_at']


class CardComment(models.Model):
    """Model for comments on cards"""
    
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.card.title}"
    
    class Meta:
        ordering = ['created_at']


class CardDocument(models.Model):
    """Model for documents attached to cards"""
    
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='card_documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.card.title}"


class Board(models.Model):
    """Model for organizing cards into boards"""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional associations to limit cards to specific contexts
    systems = models.ManyToManyField(System, blank=True, related_name='boards')
    workflows = models.ManyToManyField(Workflow, blank=True, related_name='boards')
    scripts = models.ManyToManyField(Script, blank=True, related_name='boards')
    
    def __str__(self):
        return self.name