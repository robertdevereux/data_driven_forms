# Generated by Django 5.1 on 2025-04-11 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0006_alter_answerbasic_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='routing',
            name='totalled',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
