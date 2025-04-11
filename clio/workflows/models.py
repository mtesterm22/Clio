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