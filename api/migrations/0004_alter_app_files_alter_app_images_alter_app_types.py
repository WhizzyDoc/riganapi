# Generated by Django 4.1.4 on 2023-09-24 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_app_file_remove_app_type_app_types_image_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='files',
            field=models.ManyToManyField(blank=True, to='api.file'),
        ),
        migrations.AlterField(
            model_name='app',
            name='images',
            field=models.ManyToManyField(blank=True, to='api.image'),
        ),
        migrations.AlterField(
            model_name='app',
            name='types',
            field=models.ManyToManyField(blank=True, related_name='apps', to='api.type'),
        ),
    ]
