# Generated by Django 5.0 on 2024-01-31 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company_Staff', '0008_remove_inventory_adjustment_history_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory_adjustment',
            name='Reference_number',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
