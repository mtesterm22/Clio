# scripts/forms.py

from django import forms
from .models import Script, ScriptDocument

class ScriptForm(forms.ModelForm):
    class Meta:
        model = Script
        fields = ['name', 'description', 'location', 'systems', 'workflows', 'schedule_information', 'documentation']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'systems': forms.SelectMultiple(attrs={'size': '5'}),
            'workflows': forms.SelectMultiple(attrs={'size': '5'}),
            'schedule_information': forms.Textarea(attrs={'rows': 3}),
            'documentation': forms.Textarea(attrs={'rows': 6}),
        }

class ScriptDocumentForm(forms.ModelForm):
    class Meta:
        model = ScriptDocument
        fields = ['name', 'document', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }