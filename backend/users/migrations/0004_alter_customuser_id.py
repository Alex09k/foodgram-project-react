# Generated by Django 4.2.5 on 2023-09-17 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20230914_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
