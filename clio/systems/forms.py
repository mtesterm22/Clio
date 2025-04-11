# systems/forms.py

from django import forms
from .models import System, SystemRelationship, SystemDocument, SystemNote

class SystemForm(forms.ModelForm):
    class Meta:
        model = System
        fields = [
            'name', 'description', 'category', 'vendor', 
            'operating_system', 'support_information', 
            'contact_information', 'cost', 'cost_structure',
            'sso_methodology', 'sso_system', 'status', 
            'documentation_url'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'support_information': forms.Textarea(attrs={'rows': 4}),
            'contact_information': forms.Textarea(attrs={'rows': 4}),
        }


class SystemRelationshipForm(forms.ModelForm):
    class Meta:
        model = SystemRelationship
        fields = ['source_system', 'target_system', 'relationship_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SystemDocumentForm(forms.ModelForm):
    class Meta:
        model = SystemDocument
        fields = ['name', 'document', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SystemNoteForm(forms.ModelForm):
    class Meta:
        model = SystemNote
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }