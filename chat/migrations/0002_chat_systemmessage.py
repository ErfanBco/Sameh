# Generated by Django 4.2.3 on 2023-10-25 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='systemMessage',
            field=models.BooleanField(default=False),
        ),
    ]
