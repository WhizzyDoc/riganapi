# Generated by Django 4.1.4 on 2023-10-05 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_alter_chat_starred_by_alter_groupchat_starred_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='file_description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='file description'),
        ),
        migrations.AddField(
            model_name='groupchat',
            name='file_description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='file description'),
        ),
    ]