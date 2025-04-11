# workflows/forms.py

from django import forms
from .models import Workflow, WorkflowDocument

class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['name', 'description', 'systems', 'scripts', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'systems': forms.SelectMultiple(attrs={'size': '5'}),
            'scripts': forms.SelectMultiple(attrs={'size': '5'}),
        }

class WorkflowDocumentForm(forms.ModelForm):
    class Meta:
        model = WorkflowDocument
        fields = ['name', 'document', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }