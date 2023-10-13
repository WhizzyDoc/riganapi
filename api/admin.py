from django.contrib import admin
from .models import Profile, Category, Type, App, File, Image, Comment, \
    Group, GroupChat, Chat, ChatRoom, Friend, Status, Notification, GPTRoom, \
        GPTChat

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'firstName', 'lastName', 'email', 'phone_number', 'gender', 'is_premium_user', 'online']
    list_filter = ['is_premium_user', 'online']
    list_per_page = 20

@admin.register(GPTRoom)
class GPTRoomAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'room_id', 'created']
    list_filter = ['user']
    list_per_page = 20

@admin.register(GPTChat)
class GPTChatAdmin(admin.ModelAdmin):
    list_display = ['room', 'prompt', 'reply', 'date']
    list_filter = ['room']
    list_per_page = 20

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['app', 'title', 'type', 'active', 'date']
    list_filter = ['app', 'active', 'type']
    list_editable = ['active', 'type']
    list_per_page = 20   

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created', 'updated']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    
@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created', 'updated']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    
@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'version', 'is_paid', 'price', 'developer', 'slug', 'updated']
    list_filter = ['category', 'version', 'is_paid']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'category']
    list_per_page = 20
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'app', 'comment', 'star', 'active']
    list_filter = ['app']
    list_editable = ['app', 'active']
    list_per_page = 20

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'type', 'locked', 'active', 'created', 'updated']
    list_filter = ['type', 'locked', 'active']
    list_editable = ['type', 'locked', 'active']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 30
    
@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ['group', 'sender', 'message', 'date']
    list_filter = ['group']
    list_per_page = 50
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'message', 'date', 'seen']
    list_filter = ['seen', 'room']
    list_editable = ['seen']
    list_per_page = 50
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['title', 'last_message', 'created', 'updated']
    list_per_page = 30
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['owner', 'status', 'background', 'font_family', 'font_weight', 'date']
    list_per_page = 20
 
admin.site.register(File)
admin.site.register(Image)
admin.site.register(Friend)
