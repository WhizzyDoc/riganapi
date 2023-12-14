from rest_framework import generics, viewsets
from .models import Profile, App, Category, Type, Comment, Group, GroupChat, Chat, ChatRoom, Friend, Status, \
    Notification, GPTRoom, GPTChat
from .serializers import ProfileSerializer, UserSerializer, CategorySerializer, AppSerializer,\
    TypeSerializer, CommentSerializer, GroupSerializer, GroupChatSerializer, ChatSerializer, \
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
from .encrypt_utils import encrypt, decrypt
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import FileResponse
from django.utils.text import slugify
import openai
import random
import string
import secrets

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
    
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_groups(self, request, *args, **kwargs):
        user_arg = self.request.query_params.get('username')
        user = User.objects.get(username=user_arg)
        profile = Profile.objects.get(user=user)
        try:
            groups = Group.objects.filter(members=profile)
            if groups.exists():
                return Response({
                    'status': 'success',
                    'data': [GroupSerializer(group).data for group in groups],
                })
            else:
                return Response({
                    'status': 'error1',
                    'data': 'You don\'t have any group yet',
                })
        except:
            return Response({
                'status': 'error',
                'message': "Invalid login credentials",
            })
    @action(detail=True,
            methods=['get'])
    def get_chats(self, request, *args, **kwargs):
        group = self.get_object()
        user_arg = int(self.request.query_params.get('user_id'))
        profile = Profile.objects.get(id=user_arg)
        chats = GroupChat.objects.filter(group=group)
        for chat in chats:
            if chat.sender != profile:
                if chat.seen_by != profile:
                    chat.seen_by.add(profile)
                    chat.seen = True
                    chat.save()
            else:
                if chat.seen_by != profile:
                    chat.seen_by.add(profile)
                    chat.save()
        for c in chats:
            c.message = decrypt(c.message)
        return Response({
            'status': 'success',
            'data': [GroupChatSerializer(chat).data for chat in chats],
        }) 
    @action(detail=True,
            methods=['post'])
    def send_group_chat(self, request, *args, **kwargs):
        group = self.get_object()
        sender = int(request.POST.get('sender_id'))
        message = ''
        file_des = ''
        file = None
        if request.POST.get('message'):
            message = request.POST.get('message')
        if request.FILES.get('file'):
            file = request.FILES.get('file')
            fileName = file.name
            fileSize = file.size
            size = int(fileSize / 1024)
            s = f'{str(size)}KB'
            if size > 1024:
                size = int(size / 1024)
                s = f'{str(size)}MB'
            file_des = f'{fileName}\t{s}'
        try:
            sender_p = Profile.objects.get(id=sender)
            new_chat = GroupChat.objects.create(group=group, sender=sender_p, message=encrypt(message), files=file, file_description=file_des)
            new_chat.seen_by.add(sender_p)
            new_chat.save()
            if message != '':
                group.last_message = f'{sender_p.user.username}: {message}'
                group.save()
            elif message == '' and file_des != '':
                group.last_message = f'{sender_p.user.username} sent a file: {file_des}'
                group.save()
            return Response({
                'status': 'success',
                'message': 'message sent successfully'
            })
        except:
            return Response({
                'status': 'error',
                'message': 'error sending message'
            })
    @action(detail=False,
            methods=['post'])
    def create_group(self, request, *args, **kwargs):
        user = int(request.POST.get('user_id'))
        name = request.POST.get('name')
        description = request.POST.get('description')
        type =  request.POST.get('type')
        slug = slugify(name)
        image = request.FILES.get('image', None)
        if image is None:
            image = None
        else:
            image = image
        try:
            profile = Profile.objects.get(id=user)
            new_group = Group.objects.create(title=name, slug=slug, description=description, type=type, image=image)
            new_group.last_message = f'{profile.user.username} created this group.'
            new_group.admins.add(profile)
            new_group.members.add(profile)
            new_group.save()
            return Response({
                'status': 'success',
                'message': 'group created successfully'
            })
        except:
            return Response({
                'status': 'error',
                'message': 'error occured while creating group'
            })
            
    @action(detail=True,
            methods=['post'])
    def delete_chat(self, request, *args, **kwargs):
        group = self.get_object()
        chat_id = int(request.POST.get('chat_id'))
        profile_id = int(request.POST.get('profile_id'))
        try:
            chat = GroupChat.objects.get(id=chat_id, group=group)
            profile = Profile.objects.get(id=profile_id)
            if group.last_message == f'{profile.user.username}: {chat.message}':
                group.last_message = f'This message was deleted'
                group.save()
            chat.delete()
            return Response({
                'status': 'success',
                'message': 'message deleted successfully'
            })
        except:
            return Response({
                'status': 'error',
                'message': 'error deleting message'
            }) 
    @action(detail=True,
            methods=['post'])
    def star_chat(self, request, *args, **kwargs):
        group = self.get_object()
        chat_id = int(request.POST.get('chat_id'))
        profile_id = int(request.POST.get('profile_id'))
        try:
            chat = GroupChat.objects.get(id=chat_id, group=group)
            profile = Profile.objects.get(id=profile_id)
            if profile not in chat.starred_by.all():
                chat.starred_by.add(profile)
                return Response({
                    'status': 'success-star',
                    'message': 'message starred successfully'
                })
            elif profile in chat.starred_by.all():
                chat.starred_by.remove(profile)
                return Response({
                    'status': 'success-unstar',
                    'message': 'message unstarred successfully'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'error starring message'
            }) 
    @action(detail=True,
            methods=['get'])
    def get_new_group_chats(self, request, *args, **kwargs):
        group = self.get_object()
        user = int(self.request.query_params.get('user_id'))
        try:
            profile = Profile.objects.get(id=user)
            new_chats = GroupChat.objects.exclude(seen_by=profile).filter(group=group)
            if new_chats.exists():
                return Response({
                    'status': 'success',
                    'message': 'new messages found',
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'no new chats'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'error fetching messages'
            }) 
    @action(detail=False,
            methods=['get'])
    def get_new_chats(self, request, *args, **kwargs):
        user = int(self.request.query_params.get('user_id'))
        try:
            profile = Profile.objects.get(id=user)
            groups = Group.objects.filter(members=profile)
            new_chats = False
            numb = 0
            for group in groups:
                for chat in group.group_chat.all():
                    if profile not in chat.seen_by.all():
                        new_chats = True
                        numb += 1
                    else:
                        pass
            if new_chats == True:
                return Response({
                    'status': 'success',
                    'message': 'new messages found',
                    'number': numb
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'no new chats'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'error fetching messages'
            })
    @action(detail=False,
            methods=['get'])
    def search_group(self, request, *args, **kwargs):
        query = self.request.query_params.get('query')
        groups = Group.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))[:20]
        if groups.exists():
            return Response({
                'status': 'success',
                'data': [GroupSerializer(group).data for group in groups],
            })
        else:
             return Response({
                'status': 'error',
                'message': 'No group found',
            })
    @action(detail=True,
            methods=['post'])
    def join_group(self, request, *args, **kwargs):
        group = self.get_object()
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        try:
            profile = Profile.objects.get(id=user_id)
            if action == 'join':
                group.members.add(profile)
                group.save()
                return Response({
                    'status': 'success',
                    'message': 'group joined',
                })
            elif action == 'leave':
                group.members.remove(profile)
                if profile in group.admins.all():
                    group.admins.remove(profile)
                    group.save()
                group.save()
                return Response({
                    'status': 'success',
                    'message': 'group exited',
                })
                
        except:
             return Response({
                'status': 'error',
                'message': f'Error {action}ing group',
            })

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_notifications(self, request, *args, **kwargs):
        note_arg = self.request.query_params.get('app_type')
        notes = Notification.objects.filter(Q(app=note_arg) | Q(app='All') & Q(active=True))
        if notes.exists():
            return Response({
                'status': 'success',
                'message': 'notifications found',
                'data': [NotificationSerializer(note).data for note in notes],
            })
        else:
            return Response({
                'status': 'error',
                'message': 'no notification'
            })
    @action(detail=True,
            methods=['get'])
    def view_notification(self, request, *args, **kwargs):
        note = self.get_object()
        user = int(self.request.query_params.get('user_id'))
        try:
            profile = Profile.objects.get(id=user)
            if profile not in note.seen_by.all():
                note.seen_by.add(profile)
                note.save()
            return Response({
                'status': 'success',
                'message': 'notification viewed',
                'data': NotificationSerializer(note).data
            })
        except:
            return Response({
                'status': 'error',
                'message': 'Error occured'
            })
    @action(detail=False,
            methods=['get'])
    def get_new_notifications(self, request, *args, **kwargs):
        user = int(self.request.query_params.get('user_id'))
        note_arg = self.request.query_params.get('app_type')
        profile = Profile.objects.get(id=user)
        notes = Notification.objects.filter(Q(app=note_arg) | Q(app='All') & Q(active=True))
        if notes.exists():
            new_notes_number = 0
            for note in notes:
                if profile not in note.seen_by.all():
                    new_notes_number += 1
                else:
                    new_notes_number += 0
            if new_notes_number > 0:
                return Response({
                    'status': 'success',
                    'message': 'new notifications found',
                    'number': new_notes_number
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'no new notifications'
                })
        else:
            return Response({
                'status': 'error',
                'message': 'error fetching notifications'
            })

class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_chatrooms(self, request, *args, **kwargs):
        user_arg = self.request.query_params.get('username')
        user = User.objects.get(username=user_arg)
        profile = Profile.objects.get(user=user)
        chatrooms = ChatRoom.objects.filter(members=profile)
        return Response({
            'status': 'success',
            'data': [ChatRoomSerializer(room).data for room in chatrooms],
        })
    @action(detail=True,
            methods=['get'])
    def get_other_user(self, request, *args, **kwargs):
        room = self.get_object()
        user_arg = int(self.request.query_params.get('user_id'))
        user = Profile.objects.get(id=user_arg)
        other_user = None
        for u in room.members.all():
            if u.id != user_arg:
                other_user = u
        return Response({
            'status': 'success',
            'data': ProfileSerializer(other_user).data
        })
    @action(detail=False,
            methods=['get'])
    def find_chatroom(self, request, *args, **kwargs):
        user_id = int(self.request.query_params.get('user_id'))
        f_id = int(self.request.query_params.get('friend_id'))
        profile = Profile.objects.get(id=user_id)
        friend = Profile.objects.get(id=f_id)
        c_room = None
        try:
            rooms = ChatRoom.objects.filter(members=profile)
            if rooms.exists():
                for room in rooms:
                    if room.members.filter(id=friend.id).exists():
                        c_room = room
                    else:
                        pass
                if c_room is not None:
                    return Response({
                        'status': 'success',
                        'data': ChatRoomSerializer(c_room).data
                    })
                else:
                    try:
                        new_room = ChatRoom.objects.create(title=f'{profile.user.username}-{friend.user.username}', 
                                                        last_message='click to start chatting')
                        new_room.members.add(profile)
                        new_room.members.add(friend)
                        new_room.save()
                        return Response({
                            'status': 'success',
                            'data': ChatRoomSerializer(new_room).data
                        })
                    except:
                        return Response({
                            'status': 'error',
                            'message': 'Error occured. Please try again.'
                        })
                    
            else:
                try:
                    new_room = ChatRoom.objects.create(title=f'{profile.user.username}-{friend.user.username}', 
                                                       last_message='click to start chatting')
                    new_room.members.add(profile)
                    new_room.members.add(friend)
                    new_room.save()
                    return Response({
                        'status': 'success',
                        'data': ChatRoomSerializer(new_room).data
                    })
                except:
                    return Response({
                        'status': 'error',
                        'message': 'Error occured. Please try again.'
                    })
        except:
            return Response({
                'status': 'error',
                'message': 'Error occured.'
            })
    @action(detail=True,
            methods=['get'])
    def get_chats(self, request, *args, **kwargs):
        room = self.get_object()
        user_id = self.request.query_params.get('user_id')
        profile = Profile.objects.get(id=user_id)
        blocked = False
        for m in room.members.all():
            if m != profile:
                f = Friend.objects.get(user=m)
                if profile in f.blocked_friends.all():
                    blocked = True
                else:
                    blocked = False
            else:
                pass
        chats = Chat.objects.filter(room=room)
        for chat in chats:
            if chat.sender != profile:
                if chat.seen_by != profile:
                    chat.seen_by.add(profile)
                    chat.seen = True
                    chat.save()
            else:
                if chat.seen_by != profile:
                    chat.seen_by.add(profile)
                    chat.save()
        for c in chats:
            c.message = decrypt(c.message)
        return Response({
            'status': 'success',
            'blocked': blocked,
            'data': [ChatSerializer(chat).data for chat in chats],
        }) 
    @action(detail=True,
            methods=['post'])
    def send_dm_chat(self, request, *args, **kwargs):
        room = self.get_object()
        sender = int(request.POST.get('sender_id'))
        message = ''
        file_des = ''
        file = None
        if request.POST.get('message'):
            message = request.POST.get('message')
        if request.FILES.get('file'):
            file = request.FILES.get('file')
            fileName = file.name
            fileSize = file.size
            size = int(fileSize / 1024)
            s = f'{str(size)}KB'
            if size > 1024:
                size = int(size / 1024)
                s = f'{str(size)}MB'
            file_des = f'{fileName}\t{s}'
        try:
            sender_p = Profile.objects.get(id=sender)
            new_chat = Chat.objects.create(room=room, sender=sender_p, message=encrypt(message), files=file, file_description=file_des)
            new_chat.seen_by.add(sender_p)
            new_chat.save()
            if message != '':
                room.last_message = message
                room.save()
            elif message == '' and file_des != '':
                room.last_message = f'file: {file_des}'
                room.save()
            return Response({
                'status': 'success',
                'message': 'message sent successfully'
            })
        except:
            return Response({
                'status': 'error',
                'message': 'error sending message'
            })
    @action(detail=True,
            methods=['post'])
    def delete_chat(self, request, *args, **kwargs):
        room = self.get_object()
        chat_id = int(request.POST.get('chat_id'))
        profile_id = int(request.POST.get('profile_id'))
        try:
            chat = Chat.objects.get(id=chat_id, room=room)
            profile = Profile.objects.get(id=profile_id)
            if room.last_message == chat.message:
                room.last_message = f'This message was deleted'
                room.save()
            chat.delete()
            return Response({
                'status': 'success',
                'message': 'message deleted successfully'
            })
        except:
            return Response({
                'status': 'error',
                'message': 'error deleting message'
            }) 
    @action(detail=True,
            methods=['post'])
    def star_chat(self, request, *args, **kwargs):
        room = self.get_object()
        chat_id = int(request.POST.get('chat_id'))
        profile_id = int(request.POST.get('profile_id'))
        try:
            chat = Chat.objects.get(id=chat_id, room=room)
            profile = Profile.objects.get(id=profile_id)
            if profile not in chat.starred_by.all():
                chat.starred_by.add(profile)
                return Response({
                    'status': 'success-star',
                    'message': 'message starred successfully'
                })
            elif profile in chat.starred_by.all():
                chat.starred_by.remove(profile)
                return Response({
                    'status': 'success-unstar',
                    'message': 'message unstarred successfully'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'error starring message'
            }) 
    @action(detail=True,
            methods=['get'])
    def get_new_room_chats(self, request, *args, **kwargs):
        room = self.get_object()
        user = int(self.request.query_params.get('user_id'))
        try:
            profile = Profile.objects.get(id=user)
            new_chats = Chat.objects.exclude(seen_by=profile).filter(room=room)
            if new_chats.exists():
                return Response({
                    'status': 'success',
                    'message': 'new messages found',
                    'id': room.id,
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'no new chats'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'error fetching messages'
            }) 
    @action(detail=False,
            methods=['get'])
    def get_new_chats(self, request, *args, **kwargs):
        user = int(self.request.query_params.get('user_id'))
        try:
            profile = Profile.objects.get(id=user)
            rooms = ChatRoom.objects.filter(members=profile)
            new_chats = False
            new_chats_number = 0
            for room in rooms:
                for chat in room.room_chats.all():
                    if profile not in chat.seen_by.all():
                        new_chats = True
                        new_chats_number += 1
                    else:
                        new_chats_number += 0
            if new_chats == True:
                return Response({
                    'status': 'success',
                    'message': 'new messages found',
                    'number': new_chats_number
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'no new chats'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'error fetching messages'
            })
    @action(detail=False,
            methods=['get'])
    def download_file(self, request, *args, **kwargs):
        file_path = self.request.query_params.get('path')
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{slugify(file_path)}"'
        return response

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['post'])
    def get_profile(self, request, *args, **kwargs):
        username = sterilize(request.data.get('username'))
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                profile = Profile.objects.get(user=user)
                return Response({
                    'status': 'success',
                    'data': ProfileSerializer(profile).data,
                    'username': user.username,
                })
            else:
                logout(request, user)
                return Response({
                    'status': 'error',
                    'message': "Your account has been disabled",
                })
        else:
            return Response({
                'status': 'error',
                'message': "Invalid login credentials",
            })
    @action(detail=True,
            methods=['get'])
    def get_user_profile(self, request, *args, **kwargs):
        user = self.get_object()
        user_id = int(self.request.query_params.get('user_id'))
        profile = Profile.objects.get(id=user_id)
        if user is not None:
            groups = Group.objects.filter(members=user)
            friend_list = Friend.objects.get(user=user)
            my_friends = Friend.objects.get(user=profile)
            return Response({
                'status': 'success',
                'data': ProfileSerializer(user).data,
                'groups': [GroupSerializer(group).data for group in groups],
                'friends': FriendSerializer(friend_list).data,
                'my_friends': FriendSerializer(my_friends).data,
            })
        else:
            return Response({
                'status': 'error',
                'message': "Sorry, this user does not exist.",
            })
    @action(detail=True,
            methods=['post'])
    def user_option(self, request, *args, **kwargs):
        f = self.get_object()
        user_id = int(request.POST.get('user_id'))
        profile = Profile.objects.get(id=user_id)
        action = request.POST.get('action')
        try:
            fr = Friend.objects.get(user=profile)
            if action == 'add':
                fr.active_friends.add(f)
                fr.save()
            elif action == 'accept':
                fr.active_friends.add(f)
                fr.save()
            elif action == 'block':
                fr.active_friends.remove(f)
                fr.blocked_friends.add(f)
                fr.save()
            elif action == 'unblock':
                fr.active_friends.add(f)
                fr.blocked_friends.remove(f)
                fr.save()
            return Response({
                'status': 'success',
                'message': f'successfully {action}ed {f.user.username}!'
            })
        except:
            return Response({
                'status': 'error',
                'message': f'error occured while {action}ing {f.user.username}!'
            })
        
    @action(detail=True,
            methods=['get'])
    def get_friends(self, request, *args, **kwargs):
        profile = self.get_object()
        try:
            friend_list = Friend.objects.get(user=profile)
            friends = friend_list.active_friends.all()
            return Response({
                'status': 'success',
                'data': [ProfileSerializer(user).data for user in friends]
            })
        except:
            return Response({
                'status': 'error',
                'message': "You don\'t have any friends yet.",
            })
    @action(detail=False,
            methods=['post'])
    def update_profile_image(self, request, *args, **kwargs):
        image = request.FILES['image']
        username = request.POST['username']
        try:
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)
            try:
                profile.image = image
                profile.save()
                return Response({
                    'status': 'success',
                    'message': "Profile Image updated Successfully"
                })
            except:
                return Response({
                    'status': 'error',
                    'message': "Unsupported file format, kindly upload an image file"
                })
        except:
            return Response({
                'status': 'error',
                'message': "Sorry, this user does not exist. kindly log back in or contact administrator"
            })
    @action(detail=False,
            methods=['post'])
    def account_options(self, request, *args, **kwargs):
        username = request.data.get('username')
        option = request.data.get('option')
        try:
            user = User.objects.get(username=username)
            if option == 'deactivate':
                user.is_active = False
                user.save()
                return Response({
                    'status': 'success',
                    'message': 'Account has been deactivated'
                })
            elif option == 'delete':
                user.delete()
                return Response({
                    'status': 'success',
                    'message': 'Account has been deleted'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error occured!'
            })  
    @action(detail=False,
            methods=['post'])
    def update_profile(self, request, *args, **kwargs):
        firstName = request.data.get('firstName')
        lastName = request.data.get('lastName')
        email = request.data.get('email')
        bio = request.data.get('bio')
        api_key = request.data.get('api_key')
        phoneNumber = request.data.get('phoneNumber')
        username = sterilize(request.data.get('username'))
        pin = request.data.get('pin')
        if checkPin(pin, 4) == False:
            return Response({
                'status': 'error',
                'message': "PIN should be 4 digits"
            })
        if not pin.isdigit():
            return Response({
                'status': 'error',
                'message': "Invalid PIN. PIN should contain only numbers."
            })
        try:
            user = User.objects.get(username=username)
            user.username = username
            user.save()
            profile = Profile.objects.get(user=user)
            profile.firstName = firstName
            profile.lastName = lastName
            profile.phone_number = phoneNumber
            profile.bio = bio
            profile.openai_key = api_key
            profile.pin = pin
            if is_valid_email(email):
                profile.email = email
                profile.save()
                return Response({
                    'status': 'success',
                    'message': "Profile updated Successfully",
                    'data': ProfileSerializer(profile).data
                })
            else:
                return Response({
                'status': 'error',
                'message': "Invalid Email"
            })
        except:
            return Response({
                'status': 'error',
                'message': "Sorry, this user does not exist. kindly log back in or contact administrator"
            })
    @action(detail=False,
            methods=['post'])
    def forgot_password(self, request, *args, **kwargs):
        username = sterilize(request.data.get('username'))
        pin = sterilize(request.data.get('recoveryPin'))
        try:
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)
            if profile.pin == pin:
                return Response({
                    'status': 'success',
                    'message': "You can now create a new password"
                })
            else:
                return Response({
                    'status': 'error',
                    'message': "Invalid username or PIN"
                })
        except:
            return Response({
                'status': 'error',
                'message': "Invalid username or PIN"
            })
    @action(detail=False,
            methods=['post'])
    def create_new_password(self, request, *args, **kwargs):
        username = sterilize(request.data.get('username'))
        password = request.data.get('password').strip()
        if is_valid_password(password):
            try:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                return Response({
                    'status': 'success',
                    'message': "Password reset successfully, you can now login"
                })
            except:
                return Response({
                    'status': 'error',
                    'message': "Error occured. please try again"
                })
        else:
            return Response({
                'status': 'error',
                'message': "Invalid password. password must contain at least 8 characters and also contain digits"
            })
    @action(detail=False,
            methods=['post'])
    def authentication(self, request, *args, **kwargs):
        username = sterilize(request.data.get('username'))
        password = request.data.get('password').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                profile = get_object_or_404(Profile, user=user)
                profile.online = True
                profile.save()
                # apps = App.objects.all()
                # for app in apps:
                #    Comment.objects.create(name="WhizzyDoc", app=app, comment="I love this app", star=5)
                return Response({
                    'status': "success",
                    "message": "login successful",
                    "profile": ProfileSerializer(profile).data,
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
    def logout_view(self, request, *args, **kwargs):
        username = sterilize(request.data.get('username'))
        password = request.data.get('password').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                logout(request)
                profile = get_object_or_404(Profile, user=user)
                profile.online = False
                profile.save()
                #apps = App.objects.all()
                #for app in apps:
                #    Comment.objects.create(name="WhizzyDoc", app=app, comment="I love this app", star=5)
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
            methods=['post'])
    @csrf_exempt
    def register(self, request, *args, **kwargs):
        email = request.data.get('email')
        firstName = request.data.get('firstName')
        lastName = request.data.get('lastName')
        phoneNumber = request.data.get('phoneNumber')
        gender = request.data.get('gender')
        bio = request.data.get('bio')
        username = sterilize(request.data.get('username'))
        password = request.data.get('password').strip()
        if is_valid_username(username) and is_valid_password(password) and is_valid_email(email):
            # check if username and email does not exist
            usernames = []
            emails = []
            users = User.objects.all()
            for user in users:
                usernames.append(user.username)
                emails.append(user.email)
            if username not in usernames and email not in emails:
                # create new user
                new_user = User(username=username, email=email, first_name=firstName, last_name=lastName)
                new_user.set_password(password)
                new_user.save()
                # create a new profile for user
                profile = Profile(user=new_user, firstName=firstName, lastName=lastName, email=email, 
                                  phone_number=phoneNumber, gender=gender, bio=bio)
                profile.save()
                Friend.objects.create(user=profile)
                Status.objects.create(owner=profile, status="Welcome to iChat where you get to meet friends and families.", 
                                    background="maroon", font_family="sans-serif", font_weight="normal")
                Status.objects.create(owner=profile, status="We hope you enjoy your experience with us.", 
                                    background="navy", font_family="sans-serif", font_weight="normal")
                # return success status
                return Response({
                    'status': 'success',
                    'message': 'Registration Successful',
                    'username': username,
                    'profile': ProfileSerializer(profile).data
                })
            elif username in usernames:
                return Response({
                    'status': 'error',
                    'message': f"Username already exists.",
                })
            elif email in emails:
                return Response({
                    'status': 'error',
                    'message': f"Email {email} has already been used. Kindly use another email.",
                })
        else:
            return Response({
                'status': 'error',
                'message': f"Invalid password or username or email.",
            })
    @action(detail=False,
            methods=['get'])
    def get_my_status(self, request, *args, **kwargs):
        stats = Status.objects.all()
        time = timezone.now() - timedelta(hours=24)
        for s in stats:
            if s.date <= time:
                s.delete()
        profile_id = self.request.query_params.get('profile_id')
        profile = Profile.objects.get(id=profile_id)
        try:
            statuses = Status.objects.filter(owner=profile)
            if statuses.exists():
                return Response({
                    'status': 'success',
                    'message': 'Status found',
                    'data': [StatusSerializer(stat).data for stat in statuses],
                    'profile': ProfileSerializer(profile).data,
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'No status',
                    'profile': ProfileSerializer(profile).data,
                })
        except:
            return Response({
                'status': 'error',
                'message': 'No status',
                'profile': ProfileSerializer(profile).data,
            })
    @action(detail=False,
            methods=['get'])
    def get_other_status(self, request, *args, **kwargs):
        stats = Status.objects.all()
        profile_id = self.request.query_params.get('profile_id')
        profile = Profile.objects.get(id=profile_id)
        f = Friend.objects.get(user=profile)
        time = timezone.now() - timedelta(hours=24)
        active_statuses = []
        for s in stats:
            if s.date <= time:
                s.delete()
            else:
                s.gotten_by.add(profile)
                s.save()
        try:
            for u in f.active_friends.all():
                u_status =  Status.objects.filter(owner=u)
                if u_status.exists():
                    fr = Friend.objects.get(user=u)
                    if profile in fr.active_friends.all():
                        active_statuses.append(fr)
                    else:
                        pass
                else:
                    pass
            if len(active_statuses) > 0:
                return Response({
                    'status': 'success',
                    'message': 'Status found',
                    'data': [FriendSerializer(stat).data for stat in active_statuses],
                    'profile': ProfileSerializer(profile).data
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'No status',
                    'profile': ProfileSerializer(profile).data
                })
        except:
            return Response({
                'status': 'error',
                'message': 'No status',
                'profile': ProfileSerializer(profile).data
            })
    @action(detail=True,
            methods=['get'])
    def get_new_status(self, request, *args, **kwargs):
        profile = self.get_object()
        try:
            new_status = Status.objects.exclude(Q(gotten_by=profile) | Q(owner=profile) | Q(blocked_users=profile))
            if new_status.exists():
                count = 0
                for s in new_status:
                    count += 1
                return Response({
                    'status': 'success',
                    'message': 'new status found',
                    'number': count
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'no new status'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'error fetching statuses'
            }) 
    @action(detail=True,
            methods=['post'])
    def upload_status(self, request, *args, **kwargs):
        profile = self.get_object()
        users = Profile.objects.all()
        f = Friend.objects.get(user=profile)
        status = request.POST.get('status')
        bold = request.POST.get('bold')
        font = request.POST.get('font')
        color = request.POST.get('color')
        try:
            new_status = Status(owner=profile, status=status, background=color, 
                                font_family=font, font_weight=bold)
            """
            for user in users:
                if user not in f.active_friends.all():
                    new_status.blocked_users.add(user)
            """
            new_status.save()
            f.statuses.add(new_status)
            f.save()
            return Response({
                'status': 'success',
                'message': 'status updated successfully',
            })
        except:
            return Response({
                'status': 'error',
                'message': 'error updating status'
            }) 
    @action(detail=False,
            methods=['get'])
    def search_user(self, request, *args, **kwargs):
        query = self.request.query_params.get('query')
        users = Profile.objects.filter(Q(user__username__icontains=query) | Q(email__icontains=query) | 
                                       Q(phone_number__icontains=query) | Q(firstName__icontains=query) | 
                                       Q(lastName__icontains=query))[:20]
        if users.exists():
            return Response({
                'status': 'success',
                'data': [ProfileSerializer(user).data for user in users],
            })
        else:
             return Response({
                'status': 'error',
                'message': 'No user found',
            })

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    @action(detail=True,
            methods=['get'])
    def get_apps(self, request, *args, **kwargs):
        category = self.get_object()
        apps = App.objects.filter(category=category)
        return Response({
            'data': [AppSerializer(app).data for app in apps]
        })

class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    @action(detail=True,
            methods=['get'])
    def get_apps(self, request, *args, **kwargs):
        type = self.get_object()
        apps = type.apps.all()
        return Response({
            'data': [AppSerializer(app).data for app in apps]
        })

class AppViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_all_apps(self, request, *args, **kwargs):
        apps = App.objects.all()
        return Response({
            'data': [AppSerializer(app).data for app in apps],
        })
    @action(detail=False,
            methods=['get'])
    def filter(self, request, *args, **kwargs):
        cat_arg = self.request.query_params.get('category')
        type_arg = self.request.query_params.get('type')
        if cat_arg and type_arg:
            try:
                category = Category.objects.get(slug=cat_arg)
                try:
                    type = Type.objects.get(slug=type_arg)
                    apps = App.objects.filter(category=category, types=type)
                    return Response({
                        'status': "success",
                        "message": "apps fetched successfully",
                        'data': [AppSerializer(app).data for app in apps],
                    })
                except:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid app type',
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid category',
                })
        elif cat_arg:
            try:
                category = Category.objects.get(slug=cat_arg)
                apps = App.objects.filter(category=category)
                return Response({
                    'status': "success",
                    "message": "apps fetched successfully",
                    'data': [AppSerializer(app).data for app in apps],
                })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid category',
                })
        elif type_arg:
            try:
                type = Type.objects.get(slug=type_arg)
                apps = App.objects.filter(types=type)
                return Response({
                    'status': "success",
                    "message": "apps fetched successfully",
                    'data': [AppSerializer(app).data for app in apps],
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid app type',
                })
                
                
    @action(detail=False,
            methods=['get'])
    def filter_category_type(self, request, *args, **kwargs):
        cat_arg = int(self.request.query_params.get('category_id'))
        type_arg = int(self.request.query_params.get('type_id'))
        category = Category.objects.get(id=cat_arg)
        type = Type.objects.get(id=type_arg)
        apps = App.objects.filter(category=category, types=type)
        return Response({
            'data': [AppSerializer(app).data for app in apps],
        })
    @action(detail=False,
            methods=['get'])
    def search(self, request, *args, **kwargs):
        item = self.request.query_params.get('query')
        apps = App.objects.filter(Q(name__icontains=item) | Q(description__icontains=item))
        return Response({
            'data': [AppSerializer(app).data for app in apps],
        })
    @action(detail=True,
            methods=['get'])
    def get_related_apps(self, request, *args, **kwargs):
        app = self.get_object()
        related_apps = App.objects.filter(category=app.category).exclude(id=app.id)
        return Response({
            'data': [AppSerializer(apps).data for apps in related_apps],
        })
    @action(detail=True,
            methods=['get'])
    def get_comments(self, request, *args, **kwargs):
        app = self.get_object()
        comments = Comment.objects.filter(app=app, active=True)
        return Response({
            'data': [CommentSerializer(comment).data for comment in comments],
        })
    @action(detail=False,
            methods=['post'])
    @csrf_exempt
    def post_comment(self, request, *args, **kwargs):
        id = int(request.data.get('id'))
        rating = int(request.data.get('rating'))
        name = join(request.data.get('name'))
        comment = request.data.get('comment')
        try:
            app = App.objects.get(id=id)
            new_comment = Comment(name=name, app=app, comment=comment, star=rating)
            new_comment.save()
            return Response({
                'status': "success",
                "message": "Your comment has been added successfully",
                'data': CommentSerializer(new_comment).data
            })
        except:
            return Response({
                'status': "error",
                "message": "This app does not exist!"
            })
            

class GPTViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GPTRoom.objects.all()
    serializer_class = GPTRoomSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_gpt_rooms(self, request, *args, **kwargs):       
        user_id = int(self.request.query_params.get('user_id'))
        profile = Profile.objects.get(id=user_id)
        gpt_rooms = GPTRoom.objects.filter(user=profile)
        if gpt_rooms.exists():
            return Response({
                'status': 'success',
                'data': [GPTRoomSerializer(room).data for room in gpt_rooms]
            })
        else:
            return Response({
                'status': 'error',
                'message': 'No conversation found for this user'
            })
    @action(detail=True,
            methods=['get'])
    def get_gpt_chats(self, request, *args, **kwargs):
        room = self.get_object()
        gpt_chats = GPTChat.objects.filter(room=room)
        if gpt_chats.exists():
            for chat in gpt_chats:
                chat.prompt = decrypt(chat.prompt)
                chat.reply = decrypt(chat.reply)
            return Response({
                'status': 'success',
                'data': [GPTChatSerializer(chat).data for chat in gpt_chats]
            })
        else:
            return Response({
                'status': 'error',
                'message': 'No chat found for this conversation'
            })
    @action(detail=False,
            methods=['get'])
    def get_current_room(self, request, *args, **kwargs):
        user_id = int(self.request.query_params.get('user_id'))
        profile = Profile.objects.get(id=user_id)
        room_id = self.request.query_params.get('room_id')
        if room_id:
            room = GPTRoom.objects.get(room_id=room_id)
            chats = GPTChat.objects.filter(room=room)
            if chats.exists():
                for chat in chats:
                    chat.prompt = decrypt(chat.prompt)
                    chat.reply = decrypt(chat.reply)
                return Response({
                    'status': 'success',
                    'mode': 'existing',
                    'data': [GPTChatSerializer(chat).data for chat in chats]
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'No chat found for this conversation'
                })
        else:
            try:
                room = GPTRoom.objects.filter(user=profile).first()
                if room is not None:
                    chats = GPTChat.objects.filter(room=room)
                    if chats.exists():
                        for chat in chats:
                            chat.prompt = decrypt(chat.prompt)
                            chat.reply = decrypt(chat.reply)
                        return Response({
                            'status': 'success',
                            'mode': 'first',
                            'room': GPTRoomSerializer(room).data,
                            'data': [GPTChatSerializer(chat).data for chat in chats]
                        })
                    else:
                        return Response({
                            'status': 'error',
                            'mode': 'first',
                            'message': 'No chat found for this conversation',
                            'room': GPTRoomSerializer(room).data,
                        })
                else:
                    new_room = GPTRoom.objects.create(user=profile, title='')
                    new_room.room_id = generate(30)
                    new_room.save()
                    return Response({
                        'status': 'success',
                        'mode': 'new',
                        'data': GPTRoomSerializer(new_room).data
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Error while fetching chats'
                })
    @action(detail=False,
            methods=['post'])
    def send_gpt_chat(self, request, *args, **kwargs):
        room_id = request.POST.get('room_id')
        user_id = int(request.POST.get('user_id'))
        prompt = request.POST.get('prompt')
        profile = Profile.objects.get(id=user_id)
        room = GPTRoom.objects.get(room_id=room_id)
        api_key = profile.openai_key
        if api_key is None:
            return Response({
                'status': 'error',
                'mode': 'server',
                'message': 'No API Key found! Kindly set up your API key to continue.'
            })
        try:
            openai.api_key = api_key
            full_prompt = ''
            previous_chats = GPTChat.objects.filter(room=room)
            if previous_chats.exists():
                full_prompt = '\n'.join([f'Prompt: {chat.prompt}\nYour reply: {chat.reply}' for chat in previous_chats])
                full_prompt += '\n' + f'Prompt: {prompt}.\nthe main question is this last prompt but take note of the previous prompts and your replies in case of reference. you dont have to say it out.'
            else:
                full_prompt = prompt
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0.2,
                max_tokens=1000,
                messages = [
                    {"role": "user", "content": full_prompt}
                ]
            )
            reply = response['choices'][0]['message']['content']
            new_chat = GPTChat.objects.create(room=room, prompt=encrypt(prompt), reply=encrypt(reply))
            new_chat.save()
            room.title = prompt
            room.save()
            return Response({
                'status': 'success',
                'data': GPTChatSerializer(new_chat).data
            })
        except openai.error.OpenAIError as e:
            error_message = str(e)
            return Response({
                'status': 'error',
                'mode': 'gpt',
                'message': error_message
            })
    @action(detail=False,
            methods=['post'])
    def create_gpt_room(self, request, *args, **kwargs):       
        user_id = int(request.POST.get('user_id'))
        profile = Profile.objects.get(id=user_id)
        try:
            new_room = GPTRoom.objects.create(user=profile, title='New Conversation')
            new_room.room_id = generate(30)
            new_room.save()
            return Response({
                'status': 'success',
                'data': GPTRoomSerializer(new_room).data
            })
        except:
            return Response({
                'status': 'error',
                'message': 'Error creating a new conversation'
            })
    @action(detail=False,
            methods=['post'])
    def audio_to_text(self, request, *args, **kwargs):
        audio = request.FILES.get('audio')
