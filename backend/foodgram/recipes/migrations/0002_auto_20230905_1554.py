# Generated by Django 2.2.19 on 2023-09-05 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='Units',
            new_name='units',
        ),
    ]
