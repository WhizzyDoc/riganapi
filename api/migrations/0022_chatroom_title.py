# Generated by Django 4.1.4 on 2023-09-29 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_alter_chatroom_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Room Title'),
        ),
    ]
