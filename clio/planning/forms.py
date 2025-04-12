# planning/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import (
    Initiative, Plan, Milestone, Task, 
    ResourceAllocation, RiskRegister, PlanningDocument
)

class InitiativeForm(forms.ModelForm):
    class Meta:
        model = Initiative
        fields = [
            'name', 'description', 'status', 'priority', 
            'start_date', 'target_completion_date', 
            'budget_allocation', 'resource_requirements',
            'business_justification', 'success_criteria',
            'actual_completion_date',
            'dependencies', 'owner'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_completion_date': forms.DateInput(attrs={'type': 'date'}),
            'resource_requirements': forms.Textarea(attrs={'rows': 3}),
            'business_justification': forms.Textarea(attrs={'rows': 4}),
            'success_criteria': forms.Textarea(attrs={'rows': 3}),
        }

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['initiative', 'name', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['name', 'description', 'due_date', 'status', 'dependencies']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'name', 'description', 'milestone', 'status', 'priority',
            'assigned_to', 'estimated_hours', 'start_date', 'due_date',
            'systems', 'scripts', 'workflows', 'notes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ResourceAllocationForm(forms.ModelForm):
    class Meta:
        model = ResourceAllocation
        fields = [
            'user', 'role', 'allocation_percentage', 'start_date',
            'end_date', 'cost_center', 'estimated_cost', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class RiskRegisterForm(forms.ModelForm):
    class Meta:
        model = RiskRegister
        fields = [
            'description', 'likelihood', 'impact',
            'mitigation_strategy', 'owner', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'mitigation_strategy': forms.Textarea(attrs={'rows': 3}),
        }

class PlanningDocumentForm(forms.ModelForm):
    class Meta:
        model = PlanningDocument
        fields = [
            'name', 'document', 'document_type',
            'version', 'status', 'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }