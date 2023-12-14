from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'email', 'phone_number']
    list_per_page = 20

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'category', 'database', 'live_url', 'github_url']
    list_editable = ['category']
    list_per_page = 20

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['slug']
    
@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['slug']
    
@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['slug']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['project', 'name', 'email', 'date']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name', 'email', 'date']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'note', 'seen', 'date']
