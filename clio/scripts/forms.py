# scripts/forms.py

from django import forms
from .models import Script, ScriptDocument, ScriptSystemRelationship

class ScriptForm(forms.ModelForm):
    class Meta:
        model = Script
        fields = [
            'name', 
            'description', 
            'author', 
            'hosted_on',
            'host_location',
            'path', 
            'programming_language',
            'workflows', 
            'schedule_information', 
            'schedule_method',
            'custom_schedule_method',
            'documentation'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'workflows': forms.SelectMultiple(attrs={'size': '5'}),
            'schedule_information': forms.Textarea(attrs={'rows': 3}),
            'documentation': forms.Textarea(attrs={'rows': 6}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        schedule_method = cleaned_data.get('schedule_method')
        custom_schedule_method = cleaned_data.get('custom_schedule_method')
        
        # If 'other' is selected, custom_schedule_method is required
        if schedule_method == 'other' and not custom_schedule_method:
            self.add_error(
                'custom_schedule_method', 
                'Please specify the custom scheduling method when "Other" is selected.'
            )
        
        return cleaned_data


class ScriptSystemRelationshipForm(forms.ModelForm):
    class Meta:
        model = ScriptSystemRelationship
        fields = ['system', 'relationship_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ScriptDocumentForm(forms.ModelForm):
    class Meta:
        model = ScriptDocument
        fields = ['name', 'document', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }