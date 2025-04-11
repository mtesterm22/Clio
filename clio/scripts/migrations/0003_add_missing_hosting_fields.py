from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0001_initial'),
        ('scripts', '0002_script_hosting_and_relationships'),  # Or whatever your last migration was
    ]

    operations = [
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
        # Add any other missing fields here
    ]