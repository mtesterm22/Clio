# scripts/admin.py

from django.contrib import admin
from .models import Script, ScriptDocument

class ScriptDocumentInline(admin.TabularInline):
    model = ScriptDocument
    extra = 1

@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at')
    search_fields = ('name', 'description', 'location')
    filter_horizontal = ('systems', 'workflows')
    inlines = [ScriptDocumentInline]


@admin.register(ScriptDocument)
class ScriptDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'script', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('name', 'description', 'script__name')