# Generated by Django 5.0 on 2024-01-25 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company_Staff', '0003_chart_of_accounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory_adjustment',
            name='Status',
            field=models.CharField(choices=[('draft', 'Draft'), ('adjusted', 'Adjusted')], max_length=255, null=True),
        ),
    ]
