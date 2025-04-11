# workflows/forms.py

from django import forms
from .models import Workflow, WorkflowStep, WorkflowDocument

class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['name', 'description', 'systems', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'systems': forms.SelectMultiple(attrs={'size': '5'}),
        }

class WorkflowStepForm(forms.ModelForm):
    class Meta:
        model = WorkflowStep
        fields = ['name', 'description', 'system']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class WorkflowDocumentForm(forms.ModelForm):
    class Meta:
        model = WorkflowDocument
        fields = ['name', 'document', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }