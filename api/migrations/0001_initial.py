# Generated by Django 4.1.4 on 2023-12-19 08:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True, verbose_name='App Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('slug', models.SlugField(unique=True)),
                ('version', models.CharField(default='1.0.0', max_length=100, verbose_name='App Version')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='apps/icons/')),
                ('is_paid', models.BooleanField(default=False)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, null=True, verbose_name='Title')),
                ('slug', models.SlugField(unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, null=True, verbose_name='Group Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Group Description')),
                ('type', models.CharField(choices=[('Public', 'Public'), ('Private', 'Private')], default='Public', max_length=100, verbose_name='Group Type')),
                ('slug', models.SlugField(max_length=200, null=True, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='groups/image/', verbose_name='Group image')),
                ('locked', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('last_message', tinymce.models.HTMLField(blank=True, null=True, verbose_name='last message')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-updated'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=100, null=True, verbose_name='First Name')),
                ('lastName', models.CharField(max_length=100, null=True, verbose_name='Last Name')),
                ('email', models.EmailField(blank=True, max_length=200, null=True, verbose_name='Email')),
                ('phone_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Phone Number')),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=200, null=True, verbose_name='Gender')),
                ('bio', models.TextField(blank=True, null=True, verbose_name='Bio')),
                ('openai_key', models.CharField(blank=True, max_length=1000, null=True, verbose_name='OpenAI API Key')),
                ('image', models.ImageField(blank=True, null=True, upload_to='users/images/')),
                ('is_premium_user', models.BooleanField(default=False)),
                ('online', models.BooleanField(default=False)),
                ('pin', models.CharField(blank=True, default='1234', max_length=4, verbose_name='Recovery Pin')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['firstName'],
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True, verbose_name='name')),
                ('slug', models.SlugField(unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', tinymce.models.HTMLField(blank=True, null=True, verbose_name='status')),
                ('files', models.FileField(blank=True, null=True, upload_to='statuses/files/', verbose_name='File status')),
                ('background', models.CharField(max_length=50)),
                ('font_family', models.CharField(max_length=50)),
                ('font_weight', models.CharField(max_length=50)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('blocked_users', models.ManyToManyField(blank=True, related_name='blocked_from', to='api.profile')),
                ('gotten_by', models.ManyToManyField(blank=True, related_name='status_fetched', to='api.profile')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='status', to='api.profile')),
                ('viewed_by', models.ManyToManyField(blank=True, related_name='status_viewed', to='api.profile')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app', models.CharField(choices=[('All', 'All'), ('Appstore', 'Appstore'), ('iChat', 'iChat')], max_length=100, null=True, verbose_name='App')),
                ('type', models.CharField(choices=[('Success', 'Success'), ('Warning', 'Warning'), ('Congrats', 'Congrats'), ('Info', 'Info'), ('Danger', 'Danger')], max_length=100, null=True, verbose_name='Type')),
                ('title', models.CharField(max_length=200, null=True, verbose_name='Title')),
                ('message', tinymce.models.HTMLField(blank=True, null=True, verbose_name='message')),
                ('active', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('seen_by', models.ManyToManyField(blank=True, related_name='read_notifications', to='api.profile')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='apps/images/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='images', to='api.type')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='GroupChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', tinymce.models.HTMLField(blank=True, null=True, verbose_name='message')),
                ('files', models.FileField(blank=True, null=True, upload_to='groups/messages/files/', verbose_name='File messages')),
                ('file_description', models.CharField(blank=True, max_length=200, null=True, verbose_name='file description')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_chat', to='api.group')),
                ('seen_by', models.ManyToManyField(related_name='chats_seen', to='api.profile')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_messages', to='api.profile')),
                ('starred_by', models.ManyToManyField(blank=True, related_name='chats_starred', to='api.profile')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.AddField(
            model_name='group',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='groups_created', to='api.profile'),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='groups_joined', to='api.profile'),
        ),
        migrations.CreateModel(
            name='GPTRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255)),
                ('room_id', models.CharField(max_length=36, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gpt_rooms', to='api.profile')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='GPTChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('reply', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gpt_chats', to='api.gptroom')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('active_friends', models.ManyToManyField(blank=True, related_name='friends', to='api.profile')),
                ('blocked_friends', models.ManyToManyField(blank=True, related_name='blocked_by', to='api.profile')),
                ('statuses', models.ManyToManyField(blank=True, related_name='status_owner', to='api.status')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends_list', to='api.profile')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='apps/files/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='files', to='api.type')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('comment', models.TextField(verbose_name='Comment')),
                ('reply', models.TextField(blank=True, verbose_name='Reply')),
                ('star', models.PositiveIntegerField(default=5, verbose_name='Star Rating')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='api.app')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='Room Title')),
                ('last_message', tinymce.models.HTMLField(blank=True, null=True, verbose_name='last message')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('members', models.ManyToManyField(related_name='chats', to='api.profile')),
            ],
            options={
                'ordering': ['-updated'],
            },
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', tinymce.models.HTMLField(blank=True, null=True, verbose_name='message')),
                ('files', models.FileField(blank=True, null=True, upload_to='chats/messages/files/', verbose_name='File messages')),
                ('file_description', models.CharField(blank=True, max_length=200, null=True, verbose_name='file description')),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('seen', models.BooleanField(default=False, null=True)),
                ('room', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_chats', to='api.chatroom')),
                ('seen_by', models.ManyToManyField(related_name='chat_seen', to='api.profile')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_chats', to='api.profile')),
                ('starred_by', models.ManyToManyField(blank=True, related_name='chat_starred', to='api.profile')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.AddField(
            model_name='app',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='apps', to='api.category'),
        ),
        migrations.AddField(
            model_name='app',
            name='developer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='apps', to='api.profile'),
        ),
        migrations.AddField(
            model_name='app',
            name='files',
            field=models.ManyToManyField(blank=True, to='api.file'),
        ),
        migrations.AddField(
            model_name='app',
            name='images',
            field=models.ManyToManyField(blank=True, to='api.image'),
        ),
        migrations.AddField(
            model_name='app',
            name='types',
            field=models.ManyToManyField(blank=True, related_name='apps', to='api.type'),
        ),
    ]
