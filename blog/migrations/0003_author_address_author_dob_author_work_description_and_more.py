# Generated by Django 4.1.4 on 2023-12-19 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_project_resume_project_project_short_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='address',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='author',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='author',
            name='work_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=250, null=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interests', to='blog.author')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(blank=True, max_length=250)),
                ('job_title', models.CharField(blank=True, max_length=250)),
                ('location', models.CharField(blank=True, max_length=250)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateField(blank=True)),
                ('end_date', models.DateField(blank=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experience', to='blog.author')),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qualification', models.CharField(blank=True, max_length=250)),
                ('grade', models.CharField(blank=True, max_length=250)),
                ('institution', models.CharField(blank=True, max_length=250)),
                ('start_date', models.DateField(blank=True)),
                ('end_date', models.DateField(blank=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='education', to='blog.author')),
            ],
        ),
    ]