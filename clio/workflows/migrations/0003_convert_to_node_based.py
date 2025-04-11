# workflows/migrations/XXXX_convert_to_node_based.py

from django.db import migrations
import json

def convert_to_node_based(apps, schema_editor):
    Workflow = apps.get_model('workflows', 'Workflow')
    
    # Try to get WorkflowStep model - if it fails, we'll create empty workflows
    try:
        WorkflowStep = apps.get_model('workflows', 'WorkflowStep')
        steps_exist = True
    except LookupError:
        steps_exist = False
    
    # Create WorkflowVersion model
    WorkflowVersion = apps.get_model('workflows', 'WorkflowVersion')
    
    for workflow in Workflow.objects.all():
        # Create nodes list with start node
        nodes = [
            {
                'id': 'start',
                'type': 'start',
                'position': {'x': 250, 'y': 25},
                'data': {'label': 'Start Workflow'}
            }
        ]
        
        # Create empty edges list
        edges = []
        
        # Only try to convert steps if the model exists
        if steps_exist:
            try:
                steps = WorkflowStep.objects.filter(workflow=workflow).order_by('order')
                
                # Add step nodes
                last_node_id = 'start'
                for i, step in enumerate(steps):
                    node_id = f'step_{step.id}'
                    y_position = 125 + (i * 125)  # Vertical spacing
                    
                    # Create node
                    node_data = {
                        'id': node_id,
                        'type': 'step',
                        'position': {'x': 250, 'y': y_position},
                        'data': {
                            'label': step.name,
                            'description': step.description or '',
                        }
                    }
                    
                    # Add step-specific data if available
                    if hasattr(step, 'inputs') and step.inputs:
                        node_data['data']['inputs'] = step.inputs
                    if hasattr(step, 'outputs') and step.outputs:
                        node_data['data']['outputs'] = step.outputs
                    if hasattr(step, 'personnel') and step.personnel:
                        node_data['data']['personnel'] = step.personnel
                    if hasattr(step, 'estimated_time') and step.estimated_time:
                        node_data['data']['estimated_time'] = step.estimated_time
                    if hasattr(step, 'notes') and step.notes:
                        node_data['data']['notes'] = step.notes
                        
                    # If step has a system, add it
                    if step.system:
                        node_data['data']['system'] = step.system.name
                        node_data['data']['system_id'] = step.system.id
                    
                    nodes.append(node_data)
                    
                    # Connect to previous node
                    edges.append({
                        'id': f'e-{last_node_id}-{node_id}',
                        'source': last_node_id,
                        'target': node_id
                    })
                    
                    last_node_id = node_id
                
                # Add end node at the appropriate position
                end_node_y = 125 + (len(steps) * 125) if steps.exists() else 175
            except Exception as e:
                # If any error occurs, just set a default position
                end_node_y = 175
                last_node_id = 'start'
        else:
            # If WorkflowStep doesn't exist anymore, just set a default end position
            end_node_y = 175
            last_node_id = 'start'
            
        # Add end node
        end_node = {
            'id': 'end',
            'type': 'end',
            'position': {'x': 250, 'y': end_node_y},
            'data': {'label': 'End Workflow'}
        }
        nodes.append(end_node)
        
        # Connect last step (or start) to end
        edges.append({
            'id': f'e-{last_node_id}-end',
            'source': last_node_id,
            'target': 'end'
        })
        
        # Save to workflow
        workflow.nodes = nodes
        workflow.edges = edges
        workflow.save()

        # Also create a version record
        WorkflowVersion.objects.create(
            workflow=workflow,
            version=workflow.version,
            nodes=nodes,
            edges=edges
        )

def reverse_migration(apps, schema_editor):
    # This migration is not reversible in a meaningful way
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('workflows', '0002_workflow_edges_workflow_nodes_workflow_scripts_and_more'),  # Replace with actual previous migration
    ]

    operations = [
        migrations.RunPython(convert_to_node_based, reverse_migration),
    ]