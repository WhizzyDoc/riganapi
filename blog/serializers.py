from rest_framework import serializers
from .models import *
from api.serializers import UserSerializer
from api.serializers import ProfileSerializer
from django.contrib.auth.models import User

class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ['id', 'title']

class FrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Framework
        fields = ['id', 'title']

class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Database
        fields = ['id', 'title']
        
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'title', 'description', 'image']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'name', 'email', 'comment', 'reply', 'star', 'active', 'date']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'message', 'reply', 'date']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'note', 'date']

class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Author
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'phone_number', 'site_title',
                  'github', 'linkedin', 'twitter', 'facebook', 'instagram', 'bio', 'api_token', 'image', 'site_logo']

class ProjectSerializer(serializers.ModelSerializer):
    category = ProjectCategorySerializer(many=False, read_only=True)
    frameworks = FrameworkSerializer(many=True, read_only=True)
    database = DatabaseSerializer(many=False, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'title', 'category', 'database', 'frameworks', 'description', 'image',
                  'live_url', 'github_url', 'views', 'created']

class ResumeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=False, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    class Meta:
        model = Resume
        fields = ['id', 'author', 'projects', 'skills', 'description', 'url', 'created']