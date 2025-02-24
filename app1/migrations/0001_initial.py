# Generated by Django 5.1 on 2025-02-24 13:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScreenQuestion',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('question_type', models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('radio', 'Radio'), ('picklist', 'Pick List'), ('variant-a', 'Variant A'), ('variant-b', 'Variant B')], max_length=20)),
                ('guidance', models.TextField(blank=True, null=True)),
                ('question_text', models.TextField(blank=True, null=True)),
                ('hint', models.CharField(blank=True, max_length=255, null=True)),
                ('answer_type', models.CharField(blank=True, choices=[('text', 'Text'), ('number', 'Number'), ('date', 'Date')], max_length=20, null=True)),
                ('options', models.TextField(blank=True, null=True)),
                ('parent_screen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_questions', to='app1.screenquestion')),
            ],
        ),
        migrations.CreateModel(
            name='ScreenRouting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_id', models.CharField(max_length=100, null=True)),
                ('current_id', models.CharField(max_length=50)),
                ('answer_value', models.TextField(blank=True, null=True)),
                ('next_id', models.CharField(max_length=50)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('service_id', 'current_id', 'answer_value'), name='unique_routing_rule')],
            },
        ),
    ]
