# systems/management/commands/import_system_relationships.py

from django.core.management.base import BaseCommand
from django.db import transaction
from systems.models import System, SystemRelationship, SystemCategory, SystemStatus


class Command(BaseCommand):
    help = 'Import predefined system relationships from mockup'

    def handle(self, *args, **options):
        # Define the systems data (from the mockup's systemsData object)
        systems_data = {
            # Core Systems
            "Banner 9 Admin": {
                "inputs": ["Manual Entry", "Constituo", "External Entities (banking institutions, federal government, etc.)"],
                "type": "core",
                "group": "Core Systems"
            },
            "Active Directory": {
                "inputs": ["Identity Management Processes (Custom)"],
                "type": "core",
                "group": "Core Systems"
            },
            "Ellucian Operational Data Store (ODS)": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Core Systems"
            },
            "Ellucian Ethos": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Core Systems"
            },
            
            # Authentication & Identity
            "Azure SSO": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Authentication & Identity"
            },
            "CAS SSO": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Authentication & Identity"
            },
            "Ellucian Identity Services": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Authentication & Identity"
            },
            "Entra Connect": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Authentication & Identity"
            },
            "Microsoft Entra": {
                "inputs": ["Entra Connect"],
                "type": "core",
                "group": "Authentication & Identity"
            },
            "GlobalProtect VPN": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Authentication & Identity"
            },
            
            # Middleware & Integration
            "25Live Middleware": {
                "inputs": ["Banner 9 Admin"],
                "type": "integration",
                "group": "Middleware & Integration"
            },
            "ACM Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "ARMs Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Blackbaud Award Management Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "CourseDog Middleware": {
                "inputs": ["Banner 9 Admin"],
                "type": "integration",
                "group": "Middleware & Integration"
            },
            "CRM Advise Middleware": {
                "inputs": ["Banner 9 Admin", "Blackboard"],
                "type": "integration",
                "group": "Middleware & Integration"
            },
            "EAB Navigate Middleware": {
                "inputs": ["Banner 9 Admin"],
                "type": "integration",
                "group": "Middleware & Integration"
            },
            "eRezLife Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Follett (Course Information) Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Follett Access Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Identity Management Processes (Custom)": {
                "inputs": ["Banner 9 Admin", "Ellucian Operational Data Store (ODS)"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Library Patron Platform Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Maxient Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Distribution Lists Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Omnilert Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Presence Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Raiser's Edge Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Slate Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Transact Campus Integration (Custom)": {
                "inputs": ["Ellucian Operational Data Store (ODS)", "Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            "Zoom Integration (Custom)": {
                "inputs": ["Banner 9 Admin"],
                "type": "custom",
                "group": "Middleware & Integration"
            },
            
            # Academic Systems
            "Banner 9 Self-Service": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Academic Systems"
            },
            "Blackboard": {
                "inputs": ["Intelligent Learning Platform (ILP)"],
                "type": "core",
                "group": "Academic Systems"
            },
            "CourseDog": {
                "inputs": ["CourseDog Middleware"],
                "type": "core",
                "group": "Academic Systems"
            },
            "CRM Advise": {
                "inputs": ["CRM Advise Middleware"],
                "type": "core",
                "group": "Academic Systems"
            },
            "DegreeWorks": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Academic Systems"
            },
            "Follet (Course Information)": {
                "inputs": ["Follett (Course Information) Integration (Custom)"],
                "type": "external",
                "group": "Academic Systems"
            },
            "Follet Access": {
                "inputs": ["Follett Access Integration (Custom)"],
                "type": "external",
                "group": "Academic Systems"
            },
            "Intelligent Learning Platform (ILP)": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Academic Systems"
            },
            "Panopto": {
                "inputs": ["Blackboard"],
                "type": "core",
                "group": "Academic Systems"
            },
            "Qualtrics": {
                "inputs": ["Blackboard"],
                "type": "core",
                "group": "Academic Systems"
            },
            
            # Student Services
            "25Live": {
                "inputs": ["25Live Middleware"],
                "type": "core",
                "group": "Student Services"
            },
            "ACM": {
                "inputs": ["ACM Integration (Custom)", "Instant ID"],
                "type": "core",
                "group": "Student Services"
            },
            "ARMs": {
                "inputs": ["ARMs Integration (Custom)"],
                "type": "core",
                "group": "Student Services"
            },
            "Atlas": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Student Services"
            },
            "Beyond Graduate School": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Student Services"
            },
            "Blackbaud Award Management": {
                "inputs": ["Blackbaud Award Management Integration (Custom)"],
                "type": "core",
                "group": "Student Services"
            },
            "Door Access": {
                "inputs": ["Banner 9 Admin", "Instant ID"],
                "type": "core",
                "group": "Student Services"
            },
            "DynamicForms": {
                "inputs": ["Atlas"],
                "type": "core",
                "group": "Student Services"
            },
            "EAB Navigate": {
                "inputs": ["EAB Navigate Middleware"],
                "type": "core",
                "group": "Student Services"
            },
            "eRezLife": {
                "inputs": ["Ellucian Ethos", "eRezLife Integration (Custom)"],
                "type": "core",
                "group": "Student Services"
            },
            "Instant ID": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Student Services"
            },
            "Library Patron Platform": {
                "inputs": ["Library Patron Platform Integration (Custom)"],
                "type": "core",
                "group": "Student Services"
            },
            "Maxient": {
                "inputs": ["Maxient Integration (Custom)"],
                "type": "core",
                "group": "Student Services"
            },
            "OneCard": {
                "inputs": ["Transact Campus"],
                "type": "core",
                "group": "Student Services"
            },
            "Presence": {
                "inputs": ["Presence Integration (Custom)"],
                "type": "core",
                "group": "Student Services"
            },
            "SafeZone": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Student Services"
            },
            "SpectrumU": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Student Services"
            },
            "SurveyDig": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Student Services"
            },
            
            # Finance & Operations
            "Argos": {
                "inputs": ["Banner 9 Admin", "Ellucian Operational Data Store (ODS)", "Argos Access Control (Custom)"],
                "type": "core",
                "group": "Finance & Operations"
            },
            "Argos Access Control (Custom)": {
                "inputs": ["Ellucian Operational Data Store (ODS)"],
                "type": "custom",
                "group": "Finance & Operations"
            },
            "Automated Reporting Emails (Custom)": {
                "inputs": ["Banner 9 Admin", "Argos", "Ellucian Operational Data Store (ODS)"],
                "type": "custom",
                "group": "Finance & Operations"
            },
            "Financial Edge": {
                "inputs": ["Omatic"],
                "type": "core",
                "group": "Finance & Operations"
            },
            "FormFusion": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Finance & Operations"
            },
            "Omatic": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Finance & Operations"
            },
            "TouchNet": {
                "inputs": ["Banner 9 Admin"],
                "type": "core",
                "group": "Finance & Operations"
            },
            "Transact Campus": {
                "inputs": ["Transact Campus Integration (Custom)", "Instant ID"],
                "type": "core",
                "group": "Finance & Operations"
            },
            
            # External & Other
            "Campus Website": {
                "inputs": ["Active Directory", "Argos"],
                "type": "core",
                "group": "External & Other"
            },
            "Constituo": {
                "inputs": ["Slate"],
                "type": "external",
                "group": "External & Other"
            },
            "Manual Entry": {
                "inputs": [],
                "type": "external",
                "group": "External & Other"
            },
            "External Entities (banking institutions, federal government, etc.)": {
                "inputs": [],
                "type": "external",
                "group": "External & Other"
            },
            "Omnilert": {
                "inputs": ["Omnilert Integration (Custom)"],
                "type": "core",
                "group": "External & Other"
            },
            "Raiser's Edge NXT": {
                "inputs": ["Raiser's Edge Integration (Custom)"],
                "type": "core",
                "group": "External & Other"
            },
            "Slate": {
                "inputs": ["Slate Integration (Custom)"],
                "type": "core",
                "group": "External & Other"
            },
            
            # Microsoft Ecosystem
            "Office 365": {
                "inputs": ["Entra Connect"],
                "type": "core",
                "group": "Microsoft Ecosystem"
            },
            "Distribution Lists": {
                "inputs": ["Distribution Lists Integration (Custom)"],
                "type": "core",
                "group": "Microsoft Ecosystem"
            },
            "Zoom": {
                "inputs": ["Zoom Integration (Custom)", "Active Directory"],
                "type": "core",
                "group": "Microsoft Ecosystem"
            },
            "Account Claiming Web Application (Custom)": {
                "inputs": ["Active Directory", "Argos"],
                "type": "custom",
                "group": "Microsoft Ecosystem"
            },
            "Unifyed Portal": {
                "inputs": ["Active Directory"],
                "type": "core",
                "group": "Microsoft Ecosystem"
            }
        }
        
        # Map type names from mockup to model choices
        type_mapping = {
            'core': 'core',
            'integration': 'integration',
            'custom': 'custom',
            'external': 'external',
        }
        
        # Get or create the categories and statuses
        categories = {}
        for slug in ['core', 'integration', 'custom', 'external', 'server']:
            try:
                categories[slug] = SystemCategory.objects.get(slug=slug)
            except SystemCategory.DoesNotExist:
                # Create default categories if they don't exist
                name = {
                    'core': 'Core System', 
                    'integration': 'Integration', 
                    'custom': 'Custom Component', 
                    'external': 'External System',
                    'server': 'Server'
                }[slug]
                
                color = {
                    'core': '#d5e8f9',
                    'integration': '#e8f6e8',
                    'custom': '#fdebd0',
                    'external': '#f0d5d5',
                    'server': '#e0e0f0'
                }[slug]
                
                text_color = {
                    'core': '#3498db',
                    'integration': '#27ae60',
                    'custom': '#f39c12',
                    'external': '#c0392b',
                    'server': '#5c6bc0'
                }[slug]
                
                categories[slug] = SystemCategory.objects.create(
                    name=name,
                    slug=slug,
                    color=color,
                    text_color=text_color,
                    order=list(type_mapping.keys()).index(slug) + 1 if slug in type_mapping else 5
                )
                self.stdout.write(f"  Created category: {name}")
        
        # Get or create active status
        try:
            active_status = SystemStatus.objects.get(slug='active')
        except SystemStatus.DoesNotExist:
            active_status = SystemStatus.objects.create(
                name='Going-Concern',
                slug='active',
                color='#e8f6e8',
                text_color='#27ae60',
                is_active=True,
                order=1
            )
            self.stdout.write(f"  Created status: Going-Concern")
        
        # Map for system objects
        system_map = {}
        
        self.stdout.write('Creating systems...')
        # Create all systems first
        for name, data in systems_data.items():
            category_slug = type_mapping.get(data['type'], 'core')
            category = categories.get(category_slug, categories['core'])
            
            # Create or get system
            system, created = System.objects.update_or_create(
                name=name,
                defaults={
                    'category': category,
                    'status': active_status,
                    'description': f"Part of {data['group']}",
                }
            )
            
            system_map[name] = system
            
            if created:
                self.stdout.write(f"  Created system: {name}")
            else:
                self.stdout.write(f"  Updated system: {name}")
        
        self.stdout.write('Creating relationships...')
        # Create system relationships
        relationships_created = 0
        
        for target_name, data in systems_data.items():
            target_system = system_map.get(target_name)
            
            if not target_system:
                self.stderr.write(f"  Target system not found: {target_name}")
                continue
                
            for source_name in data['inputs']:
                source_system = system_map.get(source_name)
                
                if not source_system:
                    self.stderr.write(f"  Source system not found: {source_name}")
                    continue
                
                # Create the relationship
                relationship, created = SystemRelationship.objects.update_or_create(
                    source_system=source_system,
                    target_system=target_system,
                    relationship_type='depends_on',
                    defaults={
                        'description': f"{target_name} depends on {source_name}"
                    }
                )
                
                if created:
                    relationships_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(system_map)} systems and {relationships_created} relationships'))