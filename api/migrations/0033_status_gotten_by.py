# Generated by Django 4.1.4 on 2023-10-03 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_alter_status_blocked_users_alter_status_viewed_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='gotten_by',
            field=models.ManyToManyField(blank=True, related_name='status_fetched', to='api.profile'),
        ),
    ]