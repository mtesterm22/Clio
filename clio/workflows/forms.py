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
        fields = [
            'name', 'description', 'system',
            'inputs', 'outputs', 'personnel', 
            'estimated_time', 'notes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'inputs': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List inputs required for this step'}),
            'outputs': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List outputs produced by this step'}),
            'personnel': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List personnel or roles involved in this step'}),
            'estimated_time': forms.TextInput(attrs={'placeholder': 'e.g., 1 hour, 30 minutes, 2-3 days'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes or considerations'}),
        }

class WorkflowDocumentForm(forms.ModelForm):
    class Meta:
        model = WorkflowDocument
        fields = ['name', 'document', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }