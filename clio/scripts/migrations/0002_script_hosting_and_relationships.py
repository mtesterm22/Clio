# scripts/migrations/0002_script_hosting_and_relationships.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0001_initial'),
        ('scripts', '0001_initial'),
    ]

    operations = [
        # Rename and modify fields
        migrations.RenameField(
            model_name='script',
            old_name='location',
            new_name='path',
        ),
        
        # Add new fields
        migrations.AddField(
            model_name='script',
            name='author',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='script',
            name='programming_language',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='script',
            name='schedule_method',
            field=models.CharField(blank=True, choices=[('cron', 'Cron'), ('task_scheduler', 'Windows Task Scheduler'), ('jenkins', 'Jenkins'), ('airflow', 'Apache Airflow'), ('custom', 'Custom Scheduler'), ('manual', 'Manual Execution'), ('other', 'Other')], help_text='Method used to schedule this script', max_length=50),
        ),
        migrations.AddField(
            model_name='script',
            name='custom_schedule_method',
            field=models.CharField(blank=True, help_text="If 'Other' is selected, please specify the scheduling method", max_length=100),
        ),
        migrations.AddField(
            model_name='script',
            name='hosted_on',
            field=models.ForeignKey(blank=True, help_text='The system where this script is hosted/executed', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hosted_scripts', to='systems.system'),
        ),
        migrations.AddField(
            model_name='script',
            name='host_location',
            field=models.CharField(blank=True, help_text='Server name, VM name, or physical location where the script is hosted', max_length=255),
        ),
        
        # Modify field properties
        migrations.AlterField(
            model_name='script',
            name='path',
            field=models.CharField(blank=True, help_text='Full path to the script file', max_length=255),
        ),
        migrations.AlterField(
            model_name='script',
            name='schedule_information',
            field=models.TextField(blank=True, help_text='When and how often the script runs'),
        ),
        
        # Remove the old ManyToMany relationship
        migrations.RemoveField(
            model_name='script',
            name='systems',
        ),
        
        # Create the new relationship model
        migrations.CreateModel(
            name='ScriptSystemRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_type', models.CharField(choices=[('input', 'Input'), ('output', 'Output'), ('both', 'Both Input & Output'), ('utility', 'Utility/Support'), ('other', 'Other')], default='utility', help_text='How this script relates to the system', max_length=20)),
                ('description', models.TextField(blank=True, help_text='Details about how this script interacts with the system')),
                ('script', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='system_relationships', to='scripts.script')),
                ('system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='script_relationships', to='systems.system')),
            ],
            options={
                'verbose_name': 'Script-System Relationship',
                'verbose_name_plural': 'Script-System Relationships',
                'unique_together': {('script', 'system')},
            },
        ),
        
        # Add the new ManyToMany relationship through the relationship model
        migrations.AddField(
            model_name='script',
            name='systems',
            field=models.ManyToManyField(blank=True, related_name='related_scripts', through='scripts.ScriptSystemRelationship', to='systems.system'),
        ),
    ]