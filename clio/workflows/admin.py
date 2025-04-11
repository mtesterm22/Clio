# workflows/admin.py

from django.contrib import admin

# class WorkflowStepInline(admin.TabularInline):
#     model = WorkflowStep
#     extra = 1
#     ordering = ('order',)

# class WorkflowDocumentInline(admin.TabularInline):
#     model = WorkflowDocument
#     extra = 1

# @admin.register(Workflow)
# class WorkflowAdmin(admin.ModelAdmin):
#     list_display = ('name', 'status', 'created_at')
#     list_filter = ('status', 'created_at')
#     search_fields = ('name', 'description')
#     filter_horizontal = ('systems',)
#     inlines = [WorkflowStepInline, WorkflowDocumentInline]


# @admin.register(WorkflowStep)
# class WorkflowStepAdmin(admin.ModelAdmin):
#     list_display = ('name', 'workflow', 'order', 'system')
#     list_filter = ('workflow',)
#     search_fields = ('name', 'description', 'workflow__name')
#     ordering = ('workflow', 'order')


# @admin.register(WorkflowDocument)
# class WorkflowDocumentAdmin(admin.ModelAdmin):
#     list_display = ('name', 'workflow', 'uploaded_at')
#     list_filter = ('uploaded_at',)
#     search_fields = ('name', 'description', 'workflow__name')