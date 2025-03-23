# Generated by Django 5.1 on 2025-03-21 21:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Regime',
            fields=[
                ('regime_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('regime_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('regime_id', models.CharField(max_length=100)),
                ('schedule_id', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('complete', 'Complete')], default='not_started', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='SectionStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('regime_id', models.CharField(max_length=100)),
                ('section_id', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('complete', 'Complete')], default='not_started', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100, unique=True)),
                ('user_name', models.CharField(default='AN Other', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='AnswerBasic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('regime_id', models.CharField(max_length=100)),
                ('question_id', models.CharField(max_length=100)),
                ('answer', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'unique_together': {('user_id', 'regime_id', 'question_id')},
            },
        ),
        migrations.CreateModel(
            name='AnswerTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('regime_id', models.CharField(max_length=100)),
                ('question_id', models.CharField(max_length=100)),
                ('answer', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'unique_together': {('user_id', 'regime_id', 'question_id')},
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('question_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('question_text', models.TextField(blank=True, null=True)),
                ('question_type', models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('radio', 'Radio'), ('picklist', 'Pick List'), ('variant-a', 'Variant A'), ('variant-b', 'Variant B')], max_length=20)),
                ('guidance', models.TextField(blank=True, null=True)),
                ('hint', models.CharField(blank=True, max_length=255, null=True)),
                ('answer_type', models.CharField(blank=True, choices=[('text', 'Text'), ('number', 'Number'), ('date', 'Date')], max_length=20, null=True)),
                ('options', models.TextField(blank=True, null=True)),
                ('parent_question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_questions', to='app1.question')),
            ],
        ),
        migrations.CreateModel(
            name='Routing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_id', models.CharField(default='section_1', max_length=100)),
                ('current_question', models.CharField(max_length=50)),
                ('answer_value', models.TextField(blank=True, null=True)),
                ('next_question', models.CharField(default='Q1', max_length=50)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('section_id', 'current_question', 'answer_value'), name='unique_routing_rule')],
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('schedule_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('schedule_name', models.CharField(max_length=255)),
                ('regime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.regime')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('section_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('section_name', models.CharField(max_length=255)),
                ('section_type', models.IntegerField(default=0)),
                ('section_records', models.IntegerField(default=0)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.schedule')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.section')),
            ],
            options={
                'unique_together': {('user_id', 'section')},
            },
        ),
    ]
