# systems/models.py

from django.db import models

class System(models.Model):
    STATUS_CHOICES = [
        ('active', 'Going-Concern'),
        ('review', 'In Review'),
        ('deprecation', 'Scheduled for Deprecation'),
        ('deprecated', 'Deprecated')
    ]
    
    CATEGORY_CHOICES = [
        ('core', 'Core System'),
        ('integration', 'Integration'),
        ('custom', 'Custom Component'),
        ('external', 'External System')
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    vendor = models.CharField(max_length=255, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    support_information = models.TextField(blank=True)
    contact_information = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_structure = models.CharField(max_length=255, blank=True)
    sso_methodology = models.CharField(max_length=255, blank=True)
    sso_system = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    documentation_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_dependencies(self):
        """Returns systems this system depends on"""
        return [rel.source_system for rel in self.incoming_relationships.filter(relationship_type='depends_on')]

    def get_dependents(self):
        """Returns systems that depend on this system"""
        return [rel.target_system for rel in self.outgoing_relationships.filter(relationship_type='depends_on')]


class SystemRelationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('depends_on', 'Depends On'),
        ('provides_data_to', 'Provides Data To'),
        ('integrates_with', 'Integrates With')
    ]
    
    source_system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='outgoing_relationships')
    target_system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='incoming_relationships')
    relationship_type = models.CharField(max_length=50, choices=RELATIONSHIP_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('source_system', 'target_system', 'relationship_type')
        
    def __str__(self):
        return f"{self.source_system} {self.get_relationship_type_display()} {self.target_system}"


class SystemDocument(models.Model):
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='system_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.system.name}"


class SystemNote(models.Model):
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='system_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.system.name}"