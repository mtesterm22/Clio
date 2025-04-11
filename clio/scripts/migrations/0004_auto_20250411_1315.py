from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('scripts', '0003_add_missing_hosting_fields'),
    ]

    operations = [
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
    ]