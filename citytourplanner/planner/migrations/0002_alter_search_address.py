# Generated by Django 4.2.1 on 2023-05-29 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='address',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
