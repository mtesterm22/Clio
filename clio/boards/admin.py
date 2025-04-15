# boards/admin.py

from django.contrib import admin
from .models import Board, Card, CardComment, CardDocument

class CardCommentInline(admin.TabularInline):
    model = CardComment
    extra = 1

class CardDocumentInline(admin.TabularInline):
    model = CardDocument
    extra = 1

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'assigned_to', 'checked_out', 'created_at', 'updated_at')
    list_filter = ('type', 'status', 'checked_out', 'assigned_to', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    inlines = [CardCommentInline, CardDocumentInline]
    filter_horizontal = ('systems', 'workflows', 'scripts')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'type', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'checked_out')
        }),
        ('Primary Relationships', {
            'fields': ('primary_system', 'primary_workflow', 'primary_script')
        }),
        ('Related Items', {
            'fields': ('systems', 'workflows', 'scripts')
        }),
        ('Position', {
            'fields': ('position_x', 'position_y')
        }),
        ('Metadata', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('systems', 'workflows', 'scripts')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Related Items', {
            'fields': ('systems', 'workflows', 'scripts')
        }),
    )

@admin.register(CardComment)
class CardCommentAdmin(admin.ModelAdmin):
    list_display = ('card', 'user', 'created_at')
    list_filter = ('card', 'user', 'created_at')
    search_fields = ('text',)
    date_hierarchy = 'created_at'

@admin.register(CardDocument)
class CardDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'card', 'uploaded_by', 'uploaded_at')
    list_filter = ('card', 'uploaded_by', 'uploaded_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'uploaded_at'