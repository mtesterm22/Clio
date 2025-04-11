# workflows/migrations/0002_enhance_workflow_step.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowstep',
            name='inputs',
            field=models.TextField(blank=True, help_text='Inputs required for this step'),
        ),
        migrations.AddField(
            model_name='workflowstep',
            name='outputs',
            field=models.TextField(blank=True, help_text='Outputs produced by this step'),
        ),
        migrations.AddField(
            model_name='workflowstep',
            name='personnel',
            field=models.TextField(blank=True, help_text='Personnel or roles involved in this step'),
        ),
        migrations.AddField(
            model_name='workflowstep',
            name='estimated_time',
            field=models.CharField(blank=True, help_text='Estimated time to complete this step', max_length=100),
        ),
        migrations.AddField(
            model_name='workflowstep',
            name='notes',
            field=models.TextField(blank=True, help_text='Additional notes for this step'),
        ),
    ]