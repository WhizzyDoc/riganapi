# Generated by Django 4.1.4 on 2023-09-25 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_app_developer_app_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
    ]
