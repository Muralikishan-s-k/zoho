# Generated by Django 5.0 on 2024-02-01 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company_Staff', '0009_alter_inventory_adjustment_reference_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory_adjustment_items',
            name='Comment',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
