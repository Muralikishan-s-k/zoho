# Generated by Django 5.0 on 2024-01-31 05:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company_Staff', '0006_alter_inventory_adjustment_history_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory_adjustment_history',
            name='item',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Company_Staff.items'),
        ),
    ]
