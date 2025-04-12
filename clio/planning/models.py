# planning/models.py

from django.db import models
from django.contrib.auth.models import User
from systems.models import System
from scripts.models import Script
from workflows.models import Workflow

class Initiative(models.Model):
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(null=True, blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    budget_allocation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    resource_requirements = models.TextField(blank=True)
    business_justification = models.TextField(blank=True)
    success_criteria = models.TextField(blank=True)
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_initiatives')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_initiatives')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Plan(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ]
    
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Milestone(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('canceled', 'Canceled')
    ]
    
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='milestones')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_milestones')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ]
    
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='tasks')
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    systems = models.ManyToManyField(System, blank=True, related_name='related_tasks')
    scripts = models.ManyToManyField(Script, blank=True, related_name='related_tasks')
    workflows = models.ManyToManyField(Workflow, blank=True, related_name='related_tasks')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ResourceAllocation(models.Model):
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, null=True, blank=True, related_name='resource_allocations')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True, related_name='resource_allocations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_allocations')
    role = models.CharField(max_length=100)
    allocation_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage of time allocated to this project")
    start_date = models.DateField()
    end_date = models.DateField()
    cost_center = models.CharField(max_length=100, blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(initiative__isnull=False) | models.Q(plan__isnull=False),
                name="resource_must_be_allocated_to_initiative_or_plan"
            )
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class RiskRegister(models.Model):
    LIKELIHOOD_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ]
    
    IMPACT_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ]
    
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('mitigating', 'Mitigating'),
        ('monitoring', 'Monitoring'),
        ('resolved', 'Resolved'),
        ('accepted', 'Accepted')
    ]
    
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='risks')
    description = models.TextField()
    likelihood = models.CharField(max_length=10, choices=LIKELIHOOD_CHOICES)
    impact = models.CharField(max_length=10, choices=IMPACT_CHOICES)
    mitigation_strategy = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Risk: {self.description[:50]}..."

class PlanningDocument(models.Model):
    DOCUMENT_TYPES = [
        ('requirements', 'Requirements'),
        ('design', 'Design Document'),
        ('review', 'Review Document'),
        ('approval', 'Approval Document'),
        ('report', 'Report'),
        ('meeting_notes', 'Meeting Notes'),
        ('other', 'Other')
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded')
    ]
    
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='planning_documents/')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    version = models.CharField(max_length=20, default='1.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_planning_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(models.Q(initiative__isnull=False) | 
                       models.Q(plan__isnull=False) | 
                       models.Q(task__isnull=False)),
                name="document_must_be_attached_to_initiative_plan_or_task"
            )
        ]
    
    def __str__(self):
        return f"{self.name} v{self.version}"