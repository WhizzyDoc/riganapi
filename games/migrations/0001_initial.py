# Generated by Django 4.1.4 on 2023-09-28 04:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WordCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, null=True, verbose_name='Title')),
                ('slug', models.SlugField(unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Word Categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='WordGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100, null=True, verbose_name='word')),
                ('hint', models.CharField(max_length=500, null=True, verbose_name='hint')),
                ('meaning', models.TextField(blank=True, null=True, verbose_name='meaning')),
                ('active', models.BooleanField(default=False)),
                ('difficulty', models.CharField(blank=True, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], max_length=100, verbose_name='Difficulty')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='words', to='games.wordcategory')),
            ],
            options={
                'ordering': ['word'],
            },
        ),
    ]
