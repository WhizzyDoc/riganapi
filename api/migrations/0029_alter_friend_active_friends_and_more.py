# Generated by Django 4.1.4 on 2023-10-01 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_friend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='active_friends',
            field=models.ManyToManyField(blank=True, related_name='friends', to='api.profile'),
        ),
        migrations.AlterField(
            model_name='friend',
            name='blocked_friends',
            field=models.ManyToManyField(blank=True, related_name='blocked_by', to='api.profile'),
        ),
    ]
