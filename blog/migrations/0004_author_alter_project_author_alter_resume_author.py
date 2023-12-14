# Generated by Django 4.1.4 on 2023-12-13 20:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0003_database_framework_slug_projectcategory_slug_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, null=True, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=100, null=True, verbose_name='Last Name')),
                ('email', models.EmailField(blank=True, max_length=200, null=True, verbose_name='Email')),
                ('phone_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Phone Number')),
                ('github', models.URLField(blank=True)),
                ('linkedin', models.URLField(blank=True)),
                ('twitter', models.URLField(blank=True)),
                ('facebook', models.URLField(blank=True)),
                ('bio', tinymce.models.HTMLField(blank=True)),
                ('api_token', models.CharField(blank=True, max_length=250, verbose_name='API Key')),
                ('image', models.ImageField(blank=True, upload_to='portfolio/author/images/')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['first_name'],
            },
        ),
        migrations.AlterField(
            model_name='project',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projects_created', to='blog.author'),
        ),
        migrations.AlterField(
            model_name='resume',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resume', to='blog.author'),
        ),
    ]
