# Generated by Django 4.2.3 on 2024-08-11 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_alter_hierarchy_structureid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hierarchy',
            name='structureID',
        ),
        migrations.AddField(
            model_name='hierarchy',
            name='structure',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='employee.structure'),
            preserve_default=False,
        ),
    ]
