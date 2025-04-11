# scripts/models.py

from django.db import models
from systems.models import System
from workflows.models import Workflow

class Script(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    systems = models.ManyToManyField(System, related_name='scripts', blank=True)
    workflows = models.ManyToManyField(Workflow, related_name='scripts', blank=True)
    schedule_information = models.TextField(blank=True)
    documentation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class ScriptDocument(models.Model):
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='script_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.script.name}"