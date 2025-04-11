# systems/admin.py

from django.contrib import admin
from .models import (
    System, SystemRelationship, SystemDocument, SystemNote, 
    SystemCategory, SystemStatus, SystemAdministrator
)

class SystemDocumentInline(admin.TabularInline):
    model = SystemDocument
    extra = 1

class SystemRelationshipInline(admin.TabularInline):
    model = SystemRelationship
    fk_name = 'source_system'
    extra = 1

class SystemNoteInline(admin.TabularInline):
    model = SystemNote
    extra = 1

class SystemAdministratorInline(admin.TabularInline):
    model = SystemAdministrator
    extra = 1

@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'vendor', 'status')
    list_filter = ('category', 'status', 'vendor')
    search_fields = ('name', 'description', 'vendor')
    inlines = [
        SystemDocumentInline, 
        SystemRelationshipInline, 
        SystemNoteInline,
        SystemAdministratorInline
    ]


@admin.register(SystemRelationship)
class SystemRelationshipAdmin(admin.ModelAdmin):
    list_display = ('source_system', 'relationship_type', 'target_system')
    list_filter = ('relationship_type',)
    search_fields = ('source_system__name', 'target_system__name')


@admin.register(SystemDocument)
class SystemDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('name', 'description', 'system__name')


@admin.register(SystemNote)
class SystemNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'system', 'created_by', 'created_at')
    list_filter = ('created_at', 'system')
    search_fields = ('title', 'content', 'system__name')


@admin.register(SystemCategory)
class SystemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SystemAdministrator)
class SystemAdministratorAdmin(admin.ModelAdmin):
    list_display = ('system', 'user', 'is_primary')
    list_filter = ('is_primary', 'system')
    search_fields = ('system__name', 'user__username', 'user__first_name', 'user__last_name')