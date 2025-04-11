# Generated by Django 5.2 on 2025-04-11 00:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('systems', '0001_initial'),
        ('workflows', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('schedule_information', models.TextField(blank=True)),
                ('documentation', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('systems', models.ManyToManyField(blank=True, related_name='scripts', to='systems.system')),
                ('workflows', models.ManyToManyField(blank=True, related_name='scripts', to='workflows.workflow')),
            ],
        ),
        migrations.CreateModel(
            name='ScriptDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('document', models.FileField(upload_to='script_documents/')),
                ('description', models.TextField(blank=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('script', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='scripts.script')),
            ],
        ),
    ]
