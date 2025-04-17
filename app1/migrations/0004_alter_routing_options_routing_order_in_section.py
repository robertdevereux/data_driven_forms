# Generated by Django 5.1 on 2025-03-30 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0003_question2'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='routing',
            options={'ordering': ['section_id', 'order_in_section']},
        ),
        migrations.AddField(
            model_name='routing',
            name='order_in_section',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
