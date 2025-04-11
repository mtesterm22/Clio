# workflows/models.py

from django.db import models
from systems.models import System

class Workflow(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived')
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    systems = models.ManyToManyField(System, related_name='workflows', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class WorkflowStep(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    
    # New fields for enhanced documentation
    inputs = models.TextField(blank=True, help_text="Inputs required for this step")
    outputs = models.TextField(blank=True, help_text="Outputs produced by this step")
    personnel = models.TextField(blank=True, help_text="Personnel or roles involved in this step")
    estimated_time = models.CharField(max_length=100, blank=True, help_text="Estimated time to complete this step")
    notes = models.TextField(blank=True, help_text="Additional notes for this step")
    
    system = models.ForeignKey(System, on_delete=models.SET_NULL, null=True, blank=True, related_name='workflow_steps')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['workflow', 'order']
        
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"


class WorkflowDocument(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='workflow_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.workflow.name}"