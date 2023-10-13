from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from tinymce.models import HTMLField

# Create your models here.
GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other')
)
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    firstName = models.CharField(max_length=100, verbose_name="First Name", null=True)
    lastName = models.CharField(max_length=100, verbose_name="Last Name", null=True)
    email = models.EmailField(max_length=200, verbose_name="Email", null=True, blank=True)
    phone_number = models.CharField(max_length=200, verbose_name="Phone Number", null=True, blank=True)
    gender = models.CharField(max_length=200, verbose_name="Gender", choices=GENDER, null=True, blank=True)
    bio = models.TextField(verbose_name="Bio", null=True, blank=True)
    openai_key = models.CharField(max_length=1000, verbose_name="OpenAI API Key", null=True, blank=True)
    image = models.ImageField(upload_to="users/images/", blank=True, null=True)
    is_premium_user = models.BooleanField(default=False)
    online = models.BooleanField(default=False)
    pin = models.CharField(max_length=4, verbose_name="Recovery Pin", default="1234", blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.user.__str__()

    class Meta:
        ordering = ['firstName']

        
class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Title", null=True)
    slug = models.SlugField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = "Categories"
        
class Type(models.Model):
    name = models.CharField(max_length=100, verbose_name="name", null=True)
    slug = models.SlugField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        
class Image(models.Model):
    image = models.ImageField(upload_to="apps/images/", blank=True, null=True)
    type = models.ForeignKey(Type, on_delete=models.DO_NOTHING, related_name="images")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return f'{self.image.url} {self.type.__str__()}'

    class Meta:
        ordering = ['-created']
        
class File(models.Model):
    file = models.FileField(upload_to="apps/files/", blank=True, null=True)
    type = models.ForeignKey(Type, on_delete=models.DO_NOTHING, related_name="files")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return f'{self.file.url}  {self.type.__str__()}'

    class Meta:
        ordering = ['-created']

class App(models.Model):
    name = models.CharField(max_length=100, verbose_name="App Name", null=True)
    developer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="apps", null=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name="apps")
    types = models.ManyToManyField(Type, related_name="apps", blank=True)
    version = models.CharField(max_length=100, verbose_name="App Version", default="1.0.0")
    files = models.ManyToManyField(File, blank=True)
    icon = models.ImageField(upload_to="apps/icons/", blank=True, null=True)
    images = models.ManyToManyField(Image, blank=True)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return f'{self.name} {self.version}'

    class Meta:
        ordering = ['-created']
        
class Comment(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(verbose_name="Comment")
    reply = models.TextField(verbose_name="Reply", blank=True)
    star = models.PositiveIntegerField(verbose_name="Star Rating", default=5)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name}\'s Comment'

    class Meta:
        ordering = ['-created']

# For Chat API
# Groups Model
GROUP_CHOICES = (
    ('Public', 'Public'),
    ('Private', 'Private')
)
class Group(models.Model):
    title = models.CharField(max_length=100, verbose_name="Group Title", null=True)
    description = models.TextField(verbose_name="Group Description", null=True, blank=True)
    type = models.CharField(max_length=100, choices=GROUP_CHOICES, verbose_name="Group Type", default='Public')
    slug = models.SlugField(max_length=200, unique=True, null=True)
    image = models.ImageField(upload_to='groups/image/', blank=True, null=True, verbose_name='Group image')
    locked = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    last_message = HTMLField(verbose_name="last message", blank=True, null=True)
    admins = models.ManyToManyField(Profile, related_name="groups_created", blank=True)
    members = models.ManyToManyField(Profile, related_name="groups_joined",blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.title


class GroupChat(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_chat", null=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="group_messages", null=True)
    message = HTMLField(verbose_name="message", null=True, blank=True)
    starred_by = models.ManyToManyField(Profile, related_name="chats_starred", blank=True)
    files = models.FileField(upload_to='groups/messages/files/', blank=True, null=True, verbose_name='File messages')
    file_description = models.CharField(max_length=200, verbose_name="file description", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    seen_by = models.ManyToManyField(Profile, related_name="chats_seen")
    def __str__(self):
        return f'{self.group}'

    class Meta:
        ordering = ['date']

class ChatRoom(models.Model):
    title = models.CharField(max_length=100, verbose_name="Room Title", null=True, blank=True)
    members = models.ManyToManyField(Profile, related_name="chats")
    last_message = HTMLField(verbose_name="last message", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    def __str__(self):
        return f'Room {self.title}'

    class Meta:
        ordering = ['-updated']

class Chat(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="room_chats", null=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="user_chats", null=True)
    message = HTMLField(verbose_name="message", null=True, blank=True)
    starred_by = models.ManyToManyField(Profile, related_name="chat_starred", blank=True)
    files = models.FileField(upload_to='chats/messages/files/', blank=True, null=True, verbose_name='File messages')
    file_description = models.CharField(max_length=200, verbose_name="file description", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    seen = models.BooleanField(default=False, null=True)
    seen_by = models.ManyToManyField(Profile, related_name="chat_seen")

    def __str__(self):
        return f'{self.sender}'

    class Meta:
        ordering = ['date']

class Status(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="status", null=True)
    status = HTMLField(verbose_name="status", null=True, blank=True)
    viewed_by = models.ManyToManyField(Profile, related_name="status_viewed", blank=True)
    gotten_by = models.ManyToManyField(Profile, related_name="status_fetched", blank=True)
    blocked_users = models.ManyToManyField(Profile, related_name="blocked_from", blank=True)
    files = models.FileField(upload_to='statuses/files/', blank=True, null=True, verbose_name='File status')
    background = models.CharField(max_length=50)
    font_family = models.CharField(max_length=50)
    font_weight = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.owner}\'s status'

    class Meta:
        ordering = ['-date']
        
class Friend(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="friends_list")
    active_friends = models.ManyToManyField(Profile, blank=True, related_name="friends")
    blocked_friends = models.ManyToManyField(Profile, blank=True, related_name="blocked_by")
    statuses = models.ManyToManyField(Status, blank=True, related_name="status_owner")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.__str__()

    class Meta:
        ordering = ['created']
        
APP_TYPE = (
    ('All', 'All'),
    ('Appstore', 'Appstore'),
    ('iChat', 'iChat')
)
ALERT_TYPE = (
    ('Success', 'Success'),
    ('Warning', 'Warning'),
    ('Congrats', 'Congrats'),
    ('Info', 'Info'),
    ('Danger', 'Danger')
)
class Notification(models.Model):
    app = models.CharField(max_length=100, verbose_name="App", choices=APP_TYPE, null=True)
    type = models.CharField(max_length=100, verbose_name="Type", choices=ALERT_TYPE, null=True)
    title = models.CharField(max_length=200, verbose_name="Title", null=True)
    message = HTMLField(verbose_name="message", null=True, blank=True)
    seen_by = models.ManyToManyField(Profile, related_name="read_notifications", blank=True)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['-date']


class GPTRoom(models.Model):
    title = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="gpt_rooms")
    room_id = models.CharField(max_length=36, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created']
    
class GPTChat(models.Model):
    room = models.ForeignKey(GPTRoom, on_delete=models.CASCADE, related_name="gpt_chats")
    prompt = models.TextField()
    reply = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.room.title} - {self.date}'
    class Meta:
        ordering = ['date']