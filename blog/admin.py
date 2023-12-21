from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'email', 'phone_number', 'site_title']
    list_per_page = 20

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'category', 'database', 'live_url', 'github_url', 'views']
    list_editable = ['category', 'views']
    list_per_page = 20

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'image']
    list_editable = ['title']
    list_per_page = 20

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title']
    list_editable = ['title']
    list_per_page = 20

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['owner', 'company', 'job_title', 'start_date', 'end_date']
    list_per_page = 20

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ['owner', 'company', 'job_title', 'name', 'phone_number', 'email']
    list_per_page = 20

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['owner', 'institution', 'qualification', 'grade', 'start_date', 'end_date']
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

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['author', 'url']
    list_editable = ['url']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['project', 'name', 'email', 'star', 'active', 'date']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name', 'email', 'date']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'note', 'seen', 'date']
