# scripts/admin.py

from django.contrib import admin
from .models import Script, ScriptDocument, ScriptSystemRelationship

class ScriptDocumentInline(admin.TabularInline):
    model = ScriptDocument
    extra = 1

class ScriptSystemRelationshipInline(admin.TabularInline):
    model = ScriptSystemRelationship
    extra = 1
    autocomplete_fields = ['system']
    verbose_name = "System Relationship"
    verbose_name_plural = "System Relationships"

@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'programming_language', 'hosted_on', 'path', 'created_at')
    list_filter = ('programming_language', 'schedule_method', 'created_at', 'hosted_on')
    search_fields = ('name', 'description', 'path', 'author', 'programming_language', 'host_location')
    autocomplete_fields = ['hosted_on']
    filter_horizontal = ('workflows',)
    inlines = [ScriptSystemRelationshipInline, ScriptDocumentInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'author', 'programming_language')
        }),
        ('Hosting Information', {
            'fields': ('hosted_on', 'host_location', 'path')
        }),
        ('Workflow Relationships', {
            'fields': ('workflows',)
        }),
        ('Schedule', {
            'fields': ('schedule_information', 'schedule_method', 'custom_schedule_method')
        }),
        ('Additional Information', {
            'fields': ('documentation',)
        }),
    )


@admin.register(ScriptDocument)
class ScriptDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'script', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('name', 'description', 'script__name')


@admin.register(ScriptSystemRelationship)
class ScriptSystemRelationshipAdmin(admin.ModelAdmin):
    list_display = ('script', 'relationship_type', 'system')
    list_filter = ('relationship_type', 'system', 'script')
    search_fields = ('script__name', 'system__name', 'description')
    autocomplete_fields = ['script', 'system']