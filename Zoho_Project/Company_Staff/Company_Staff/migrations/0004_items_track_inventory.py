# Generated by Django 3.2.23 on 2024-01-22 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company_Staff', '0003_bloodgroup_comment_employee_history_payroll_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='items',
            name='track_inventory',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
