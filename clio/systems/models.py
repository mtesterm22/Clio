# systems/models.py

from django.db import models
from django.contrib.auth.models import User

class SystemCategory(models.Model):
    """Model for customizable system categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, help_text="CSS color code (e.g., #3498db)", default="#f2f2f2")
    text_color = models.CharField(max_length=20, help_text="Text color (e.g., #333333)", default="#333333")
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class for icon (e.g., fa-server)")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        verbose_name = "System Category"
        verbose_name_plural = "System Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class SystemStatus(models.Model):
    """Model for customizable system statuses"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, help_text="CSS color code (e.g., #3498db)", default="#f2f2f2")
    text_color = models.CharField(max_length=20, help_text="Text color (e.g., #333333)", default="#333333")
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class for icon (e.g., fa-check)")
    is_active = models.BooleanField(default=True, help_text="Whether systems with this status are considered active")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        verbose_name = "System Status"
        verbose_name_plural = "System Statuses"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class System(models.Model):
    """Main system model"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # ForeignKey to SystemCategory
    category = models.ForeignKey(
        SystemCategory, 
        on_delete=models.PROTECT,  # Prevent deletion of categories that are in use
        related_name='systems'
    )
    
    # ForeignKey to SystemStatus
    status = models.ForeignKey(
        SystemStatus, 
        on_delete=models.PROTECT,  # Prevent deletion of statuses that are in use
        related_name='systems'
    )
    
    vendor = models.CharField(max_length=255, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    support_information = models.TextField(blank=True)
    contact_information = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_structure = models.CharField(max_length=255, blank=True)
    
    # SSO system as ForeignKey
    sso_system = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sso_dependent_systems'
    )
    
    # Hosting system as ForeignKey
    hosting_system = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='hosted_systems'
    )
    
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
    
    @property
    def is_active(self):
        """Return whether the system is considered active based on its status"""
        return self.status.is_active


class SystemRelationship(models.Model):
    """Model for relationships between systems"""
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
    """Model for documents attached to systems"""
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='system_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.system.name}"


class SystemNote(models.Model):
    """Model for notes attached to systems"""
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='system_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.system.name}"


class SystemAdministrator(models.Model):
    """Model for system administrators"""
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='administrators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_systems')
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('system', 'user')
        
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.system.name}"