# scripts/models.py

from django.db import models
from systems.models import System
from workflows.models import Workflow

class Script(models.Model):
    SCHEDULE_METHOD_CHOICES = [
        ('cron', 'Cron'),
        ('task_scheduler', 'Windows Task Scheduler'),
        ('jenkins', 'Jenkins'),
        ('airflow', 'Apache Airflow'),
        ('custom', 'Custom Scheduler'),
        ('manual', 'Manual Execution'),
        ('other', 'Other')
    ]
    
    RELATIONSHIP_TYPE_CHOICES = [
        ('input', 'Input'),
        ('output', 'Output'),
        ('both', 'Both Input & Output'),
        ('utility', 'Utility/Support'),
        ('other', 'Other')
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.CharField(max_length=255, blank=True)
    
    # Hosting information
    hosted_on = models.ForeignKey(
        System, 
        related_name='hosted_scripts',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The system where this script is hosted/executed"
    )
    host_location = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Server name, VM name, or physical location where the script is hosted"
    )
    path = models.CharField(max_length=255, blank=True, help_text="Full path to the script file")
    
    # Technical information
    programming_language = models.CharField(max_length=100, blank=True)
    
    # System relationships are now tracked via a through model (see ScriptSystemRelationship below)
    systems = models.ManyToManyField(
        System, 
        through='ScriptSystemRelationship',
        related_name='related_scripts', 
        blank=True
    )
    workflows = models.ManyToManyField(Workflow, related_name='scripts', blank=True)
    
    # Scheduling information
    schedule_information = models.TextField(blank=True, help_text="When and how often the script runs")
    schedule_method = models.CharField(
        max_length=50, 
        choices=SCHEDULE_METHOD_CHOICES,
        blank=True,
        help_text="Method used to schedule this script"
    )
    custom_schedule_method = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="If 'Other' is selected, please specify the scheduling method"
    )
    
    # Additional information
    documentation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def get_schedule_method_display_custom(self):
        """Return the custom schedule method if 'other' is selected"""
        if self.schedule_method == 'other' and self.custom_schedule_method:
            return self.custom_schedule_method
        return self.get_schedule_method_display()


class ScriptSystemRelationship(models.Model):
    """Defines the relationship between a script and a system"""
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='system_relationships')
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='script_relationships')
    relationship_type = models.CharField(
        max_length=20,
        choices=Script.RELATIONSHIP_TYPE_CHOICES,
        default='utility',
        help_text="How this script relates to the system"
    )
    description = models.TextField(blank=True, help_text="Details about how this script interacts with the system")
    
    class Meta:
        unique_together = ('script', 'system')
        verbose_name = "Script-System Relationship"
        verbose_name_plural = "Script-System Relationships"
    
    def __str__(self):
        return f"{self.script.name} - {self.get_relationship_type_display()} - {self.system.name}"

class ScriptDocument(models.Model):
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='script_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.script.name}"