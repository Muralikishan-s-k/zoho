# Generated by Django 5.0 on 2024-01-23 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company_Staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory_adjustment',
            name='Attach_file',
            field=models.FileField(blank=True, null=True, upload_to='inventory_attachments/'),
        ),
    ]
