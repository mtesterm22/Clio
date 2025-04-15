# boards/forms.py

from django import forms
from .models import Card, CardComment, CardDocument, Board
from systems.models import System
from workflows.models import Workflow
from scripts.models import Script

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = [
            'title', 'description', 'type', 'status',
            'assigned_to', 'checked_out', 
            'primary_system', 'primary_workflow', 'primary_script',
            'systems', 'workflows', 'scripts'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'systems': forms.SelectMultiple(attrs={'class': 'select2-widget'}),
            'workflows': forms.SelectMultiple(attrs={'class': 'select2-widget'}),
            'scripts': forms.SelectMultiple(attrs={'class': 'select2-widget'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If we're editing an existing card, limit primary choices to the selected items
        if self.instance.pk:
            if self.instance.systems.exists():
                self.fields['primary_system'].queryset = self.instance.systems.all()
            else:
                self.fields['primary_system'].queryset = System.objects.none()
                
            if self.instance.workflows.exists():
                self.fields['primary_workflow'].queryset = self.instance.workflows.all()
            else:
                self.fields['primary_workflow'].queryset = Workflow.objects.none()
                
            if self.instance.scripts.exists():
                self.fields['primary_script'].queryset = self.instance.scripts.all()
            else:
                self.fields['primary_script'].queryset = Script.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that primary system is in the selected systems
        primary_system = cleaned_data.get('primary_system')
        systems = cleaned_data.get('systems')
        
        if primary_system and systems and primary_system not in systems:
            self.add_error('primary_system', 'Primary system must be one of the selected systems.')
        
        # Similar checks for workflows and scripts
        primary_workflow = cleaned_data.get('primary_workflow')
        workflows = cleaned_data.get('workflows')
        
        if primary_workflow and workflows and primary_workflow not in workflows:
            self.add_error('primary_workflow', 'Primary workflow must be one of the selected workflows.')
        
        primary_script = cleaned_data.get('primary_script')
        scripts = cleaned_data.get('scripts')
        
        if primary_script and scripts and primary_script not in scripts:
            self.add_error('primary_script', 'Primary script must be one of the selected scripts.')
        
        return cleaned_data


class CardCommentForm(forms.ModelForm):
    class Meta:
        model = CardComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }


class CardDocumentForm(forms.ModelForm):
    class Meta:
        model = CardDocument
        fields = ['name', 'document', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'description', 'systems', 'workflows', 'scripts']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'systems': forms.SelectMultiple(attrs={'class': 'select2-widget'}),
            'workflows': forms.SelectMultiple(attrs={'class': 'select2-widget'}),
            'scripts': forms.SelectMultiple(attrs={'class': 'select2-widget'}),
        }