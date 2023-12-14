from rest_framework import generics, viewsets
from api.models import Profile, Group, GroupChat, Chat, ChatRoom, Friend, Status, \
    Notification, GPTRoom, GPTChat
from api.serializers import ProfileSerializer, UserSerializer,\
    GroupSerializer, GroupChatSerializer, ChatSerializer, \
    ChatRoomSerializer, StatusSerializer, FriendSerializer, NotificationSerializer, GPTRoomSerializer, \
        GPTChatSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import action
from django.contrib.auth import login, authenticate, logout
import re
import json
from django.db.models import Q
from api.encrypt_utils import encrypt, decrypt
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import FileResponse
from django.utils.text import slugify
import openai
import random
import string

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s
def join(s):
    s = s.strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

def generate(n):
    chars = string.ascii_lowercase + string.digits
    random_combination = ''.join(random.choice(chars) for _ in range(n))
    return random_combination

def checkPin(p, n):
    if len(p.strip()) == n and p.isdigit():
        return True
    else:
        return False

def sterilize(s):
    s = ''.join(letter for letter in s if letter.isalnum())
    return s

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
        return False
    return True

def is_valid_username(username):
    pattern = r'^[a-zA-Z0-9]+$'
    if re.match(pattern, username):
        return True
    else:
        return False


# Create your views here.
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['post'])
    def admin_login(self, request, *args, **kwargs):
        username = sterilize(request.data.get('username'))
        password = request.data.get('password').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                if user.is_superuser:
                    login(request, user)
                    profile = get_object_or_404(Profile, user=user)
                    profile.online = True
                    profile.save()
                    return Response({
                        'status': "success",
                        "message": "login successful",
                        "profile": ProfileSerializer(profile).data,
                    })
                else:
                    return Response({
                    'status': 'error',
                    'message': "Unauthorized credentials",
                })
            else:
                return Response({
                    'status': 'error',
                    'message': "Your account has been disabled",
                })
        else:
            return Response({
                'status': 'error',
                'message': "Invalid login credentials",
            })
    @action(detail=False,
            methods=['post'])
    def admin_logout(self, request, *args, **kwargs):
        username = sterilize(request.data.get('username'))
        password = request.data.get('password').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                logout(request)
                profile = get_object_or_404(Profile, user=user)
                profile.online = False
                profile.save()
                return Response({
                    'status': "success",
                    "message": "You have been logged out",
                })
            else:
                profile = get_object_or_404(Profile, user=user)
                profile.online = False
                profile.save()
                return Response({
                    'status': 'error',
                    'message': "Your account has been disabled",
                })
        else:
            return Response({
                'status': 'error',
                'message': "Invalid credentials",
            })
        
    @action(detail=False,
            methods=['get'])
    def download_file(self, request, *args, **kwargs):
        file_path = self.request.query_params.get('path')
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{slugify(file_path)}"'
        return response
