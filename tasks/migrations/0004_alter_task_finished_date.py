# Generated by Django 4.2.3 on 2023-09-12 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_task_finished_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='finished_date',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
    ]
