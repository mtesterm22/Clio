# workflows/models.py

from django.db import models
from django.contrib.auth.models import User
# from systems.models import System
# from scripts.models import Script
import json

class Workflow(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived')
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    systems = models.ManyToManyField('systems.System', related_name='workflows', blank=True)
    scripts = models.ManyToManyField('scripts.Script', related_name='used_in_workflows', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Store the layout information as JSON
    nodes = models.JSONField(default=dict, blank=True)
    edges = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    def create_new_version(self):
        """Create a new version record of this workflow"""
        WorkflowVersion.objects.create(
            workflow=self,
            version=self.version,
            nodes=self.nodes,
            edges=self.edges
        )
        
        # Increment version
        self.version += 1
        self.save(update_fields=['version'])


class WorkflowVersion(models.Model):
    """Model to track workflow versions"""
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='versions')
    version = models.PositiveIntegerField()
    nodes = models.JSONField(default=dict, blank=True)
    edges = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('workflow', 'version')
        ordering = ['-version']
    
    def __str__(self):
        return f"{self.workflow.name} v{self.version}"


class WorkflowDocument(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='workflow_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.workflow.name}"