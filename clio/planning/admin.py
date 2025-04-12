# planning/admin.py

from django.contrib import admin
from .models import (
    Initiative, Plan, Milestone, Task, 
    ResourceAllocation, RiskRegister, PlanningDocument
)

class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0

class ResourceAllocationInline(admin.TabularInline):
    model = ResourceAllocation
    extra = 0
    fk_name = 'initiative'

class RiskRegisterInline(admin.TabularInline):
    model = RiskRegister
    extra = 0

class PlanningDocumentInline(admin.TabularInline):
    model = PlanningDocument
    extra = 0
    fk_name = 'initiative'

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'priority', 'owner', 'start_date', 'target_completion_date')
    list_filter = ('status', 'priority')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'
    inlines = [
        ResourceAllocationInline,
        RiskRegisterInline,
        PlanningDocumentInline,
    ]

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'initiative', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'initiative')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    inlines = [
        MilestoneInline,
        TaskInline,
    ]

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'due_date', 'status')
    list_filter = ('status', 'plan')
    search_fields = ('name', 'description')
    date_hierarchy = 'due_date'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'milestone', 'status', 'priority', 'assigned_to', 'due_date')
    list_filter = ('status', 'priority', 'plan', 'milestone')
    search_fields = ('name', 'description')
    date_hierarchy = 'due_date'
    filter_horizontal = ('systems', 'scripts', 'workflows')

@admin.register(ResourceAllocation)
class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'initiative', 'plan', 'allocation_percentage', 'start_date', 'end_date')
    list_filter = ('role', 'initiative', 'plan')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'role')
    date_hierarchy = 'start_date'

@admin.register(RiskRegister)
class RiskRegisterAdmin(admin.ModelAdmin):
    list_display = ('description', 'initiative', 'likelihood', 'impact', 'status', 'owner')
    list_filter = ('likelihood', 'impact', 'status', 'initiative')
    search_fields = ('description', 'mitigation_strategy')

@admin.register(PlanningDocument)
class PlanningDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'document_type', 'version', 'status', 'created_by', 'created_at')
    list_filter = ('document_type', 'status', 'initiative', 'plan', 'task')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'