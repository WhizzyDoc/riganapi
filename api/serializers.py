from rest_framework import serializers
from .models import Profile, Category, App, Type, Image, File, Comment, \
    Group, GroupChat, Chat, ChatRoom, Status, Friend, Notification, GPTRoom, \
        GPTChat
from games.models import WordGame, WordCategory
from django.contrib.auth.models import User

class WordCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WordCategory
        fields = ['id', 'title', 'slug']

class WordSerializer(serializers.ModelSerializer):
    category = WordCategorySerializer(many=False, read_only=True)
    class Meta:
        model = WordGame
        fields = ['id', 'word', 'hint', 'meaning', 'category', 'active', 'difficulty',
                  'active']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user','firstName', 'lastName', 'email', 'phone_number',
                  'gender', 'phone_number', 'image', 'bio', 'is_premium_user', 'pin', 'online', 'openai_key']

class NotificationSerializer(serializers.ModelSerializer):
    seen_by = ProfileSerializer(many=True, read_only=True)
    class Meta:
        model = Notification
        fields = ['id', 'app', 'title', 'type', 'message', 'active', 'seen_by', 'date']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']
        
class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'name', 'slug']
        
class ImageSerializer(serializers.ModelSerializer):
    type = TypeSerializer(many=False, read_only=True)
    class Meta:
        model = Image
        fields = ['id', 'image', 'type']
        
class FileSerializer(serializers.ModelSerializer):
    type = TypeSerializer(many=False, read_only=True)
    class Meta:
        model = File
        fields = ['id', 'file', 'type']

class AppSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    types = TypeSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    developer = ProfileSerializer(many=False, read_only=True)
    class Meta:
        model = App
        fields = ['id', 'name', 'version', 'icon', 'description', 'types', 'category',
                  'developer', 'is_paid', 'price', 'files', 'images', 'slug', 'updated']

class CommentSerializer(serializers.ModelSerializer):
    app = AppSerializer(many=False, read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'name', 'app', 'star', 'comment', 'reply', 'created']

class GroupSerializer(serializers.ModelSerializer):
    admins = ProfileSerializer(many=True)
    members = ProfileSerializer(many=True)
    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'type', 'slug', 'locked', 'active', 'image',
                  'admins', 'members', 'created', 'last_message', 'updated']

class ChatRoomSerializer(serializers.ModelSerializer):
    members = ProfileSerializer(many=True)
    class Meta:
        model = ChatRoom
        fields = ['id', 'title', 'members', 'last_message', 'created', 'updated']

class ChatSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    seen_by = ProfileSerializer(many=True)
    starred_by = ProfileSerializer(many=True)
    class Meta:
        model = Chat
        fields = ['id', 'room', 'sender', 'message', 'files', 'file_description', 'starred_by', 'date', 'seen', 'seen_by']
    def get_sender(self, obj):
        sender = obj.sender
        return ProfileSerializer(sender).data
    def get_room(self, obj):
        room = obj.room
        return ChatRoomSerializer(room).data

class GroupChatSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    seen_by = ProfileSerializer(many=True)
    starred_by = ProfileSerializer(many=True)
    group = serializers.SerializerMethodField()
    class Meta:
        group = GroupSerializer(many=False, read_only=True)
        model = GroupChat
        fields = ['id', 'group', 'sender', 'message', 'files', 'file_description', 'starred_by', 'date', 'seen_by']
    def get_sender(self, obj):
        sender = obj.sender
        return ProfileSerializer(sender).data
    def get_group(self, obj):
        sender = obj.group
        return GroupSerializer(sender).data

class StatusSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    viewed_by = ProfileSerializer(many=True)
    gotten_by = ProfileSerializer(many=True)
    blocked_users = ProfileSerializer(many=True)
    class Meta:
        model = Status
        fields = ['id', 'owner', 'status', 'background', 'font_family', 'font_weight', 'files', 
                'viewed_by', 'gotten_by', 'blocked_users', 'date']
    def get_owner(self, obj):
        owner = obj.owner
        return ProfileSerializer(owner).data

class FriendSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    active_friends = ProfileSerializer(many=True)
    blocked_friends = ProfileSerializer(many=True)
    statuses = StatusSerializer(many=True)
    class Meta:
        model = Friend
        fields = ['id', 'user', 'active_friends', 'blocked_friends', 'statuses', 'created']
    def get_user(self, obj):
        user = obj.user
        return ProfileSerializer(user).data

class GPTRoomSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(many=False)
    class Meta:
        model = GPTRoom
        fields = ['id', 'title', 'room_id', 'user', 'created']

class GPTChatSerializer(serializers.ModelSerializer):
    room = GPTRoomSerializer(many=False)
    class Meta:
        model = GPTChat
        fields = ['id', 'prompt', 'reply', 'room', 'date']
