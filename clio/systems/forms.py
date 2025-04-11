# systems/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import System, SystemRelationship, SystemDocument, SystemNote, SystemAdministrator, SystemStatus, SystemCategory

class SystemForm(forms.ModelForm):
    class Meta:
        model = System
        fields = [
            'name', 'description', 'category', 'vendor', 
            'operating_system', 'support_information', 
            'contact_information', 'cost', 'cost_structure',
            'sso_system', 'hosting_system', 'status', 
            'documentation_url'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'support_information': forms.Textarea(attrs={'rows': 4}),
            'contact_information': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limit sso_system choices to exclude self and show only active systems
        instance = kwargs.get('instance')
        # Correct approach:
        sso_systems = System.objects.filter(status__slug='active').exclude(id=instance.id if instance else None)
        self.fields['sso_system'].queryset = sso_systems
        
        # Limit hosting_system choices to exclude self and show only server category
        # Correct approach:
        hosting_systems = System.objects.filter(category__slug='server').exclude(id=instance.id if instance else None)
        self.fields['hosting_system'].queryset = hosting_systems


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


class SystemAdministratorForm(forms.ModelForm):
    class Meta:
        model = SystemAdministrator
        fields = ['user', 'is_primary', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sort users by first name and last name
        self.fields['user'].queryset = User.objects.all().order_by('first_name', 'last_name')


# Form for adding multiple administrators at once
class MultipleSystemAdministratorForm(forms.Form):
    administrators = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('first_name', 'last_name'),
        widget=forms.SelectMultiple(attrs={'class': 'select2-multiple'}),
        required=False
    )
    is_primary = forms.BooleanField(required=False, initial=False)

# Additional forms for SystemCategory and SystemStatus

class SystemCategoryForm(forms.ModelForm):
    class Meta:
        model = SystemCategory
        fields = ['name', 'slug', 'description', 'color', 'text_color', 'icon', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'color-picker'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'color-picker'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Generate slug from name if creating a new category
        if not self.instance.pk:
            self.fields['slug'].required = False
    
    def clean_name(self):
        name = self.cleaned_data['name']
        # Check uniqueness case-insensitive
        if SystemCategory.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A category with this name already exists.")
        return name
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        # If no slug provided, generate from name
        if not slug and name:
            from django.utils.text import slugify
            slug = slugify(name)
        
        # Check uniqueness
        if SystemCategory.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A category with this slug already exists.")
        return slug


class SystemStatusForm(forms.ModelForm):
    class Meta:
        model = SystemStatus
        fields = ['name', 'slug', 'description', 'color', 'text_color', 'icon', 'is_active', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'color-picker'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'color-picker'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Generate slug from name if creating a new status
        if not self.instance.pk:
            self.fields['slug'].required = False
    
    def clean_name(self):
        name = self.cleaned_data['name']
        # Check uniqueness case-insensitive
        if SystemStatus.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A status with this name already exists.")
        return name
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        # If no slug provided, generate from name
        if not slug and name:
            from django.utils.text import slugify
            slug = slugify(name)
        
        # Check uniqueness
        if SystemStatus.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A status with this slug already exists.")
        return slug