from rest_framework import generics, viewsets
from .models import *
from .serializers import *
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
from datetime import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
import random
from .utils import *
import math

# Create your views here.
def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

def generate_token():
    key = ''
    for i in range(60):
        rand_char = random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
        key += rand_char
    return key

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
    

class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['post'])
    def create_account(self, request, *args, **kwargs):
        email = request.POST.get('email')
        f_name = request.POST.get('first_name')
        l_name = request.POST.get('last_name')
        site_name = request.POST.get('site_name')
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username')
        password = request.POST.get('password')
        #check if email is valid
        if not is_valid_email(email):
            return Response({
                'status': 'error',
                'message': f"Invalid email",
            })
        if not is_valid_username(username):
            return Response({
                'status': 'error',
                'message': f"Invalid username",
            })
        if not is_valid_password(password):
            return Response({
                'status': 'error',
                'message': f"Invalid password",
            })
        try:
            # check if username and email does not exist
            usernames = []
            emails = []
            users = User.objects.all()
            for user in users:
                usernames.append(user.username)
                emails.append(user.email)
            if username not in usernames and email not in emails:
                new_user = User(email=email, first_name=f_name, last_name=l_name, username=username)
                new_user.set_password(password)
                new_user.save()
                try:
                    #print('hi')
                    api_key = generate_token()
                    #print('hello')
                    # create a new profile
                    new_profile = Author(user=new_user, email=email, first_name=f_name, last_name=l_name, api_token=api_key,
                                        phone_number=phone_number, site_title=site_name)
                    #print('he')
                    new_profile.save()
                    confirmation_email(email, f_name)
                    return Response({
                            'status': 'success',
                            'message': f'Account created successfully',
                            'data': AuthorSerializer(new_profile).data
                        })
                except:
                    return Response({
                        'status': 'error',
                        'message': f'Account created, Error generating profile',
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
        except:
            return Response({
                'status': 'error',
                'message': f'Error occured while creating account',
            })

    @action(detail=False,
            methods=['post'])
    def forgot_password(self, request, *args, **kwargs):
        email = request.POST.get('email')
        if not is_valid_email(email):
            return Response({
                'status': 'error',
                'message': f"Invalid email",
            })
        try:
            user = User.objects.get(email=email)
            if user is not None:
                token = get_random_string(length=10)
                user.set_password(token)
                user.save()
                # send email
                send_password_email(email, user.first_name, token)
                return Response({
                    'status': 'success',
                    'message': f'Password reset instructions has been sent to {email}'
                })
            else:
                return Response({
                'status': 'error',
                'message': f"Unregistered email",
            })
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f"Unregistered email",
            })

    @action(detail=False,
            methods=['post'])
    def change_password(self, request, *args, **kwargs):
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        key = request.POST.get('api_token')
        if not is_valid_password(new_password):
            return Response({
                'status': 'error',
                'message': f"Invalid new password combination",
            })
        try:
            profile = Profile.objects.get(api_token=key)
            admin = profile.user
            if admin_group in admin.groups.all():
                try:
                    user = authenticate(request, username=admin.username, password=old_password)
                    if user is not None:
                        user.set_password(new_password)
                        user.save()
                        return Response({
                            'status': "success",
                            "message": "password changed successfully",
                        })
                    else:
                        return Response({
                            'status': "error",
                            "message": "Incorrect password",
                        })
                except:
                    return Response({
                        'status': "error",
                        "message": "error while changing password",
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

    @action(detail=False,
            methods=['post'])
    def authentication(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                try:
                    admin = Author.objects.get(user=user)
                    login(request, user)
                    return Response({
                        'status': "success",
                        "message": "login successful",
                        "data": AuthorSerializer(admin).data,
                    })
                except:
                    return Response({
                        'status': 'error',
                        'message': "User is not authorized",
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
        key = request.POST.get('api_token')
        try:
            admin = Author.objects.get(api_token=key)
            if admin is not None:
                return Response({
                    'status': "success",
                    "message": "logout successful"
                })
            else:
                return Response({
                    'status': 'error',
                    'message': "User is not authorized",
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_profile(self, request, *args, **kwargs):
        key = self.request.query_params.get('api_token')
        try:
            profile = Author.objects.get(api_token=key)
            if profile is not None:
                return Response({
                    'status': "success",
                    "message": "data fetched successfully",
                    "data": AuthorSerializer(profile).data,
                })
            else:
                return Response({
                    'status': "error",
                    "message": "User not found"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    
    @action(detail=False,
            methods=['post'])
    def edit_profile(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        email = request.POST.get('email')
        f_name = request.POST.get('fname')
        l_name = request.POST.get('lname')
        site_name = request.POST.get('site_name')
        phone = request.POST.get('phone')
        github = request.POST.get('github')
        linkedin = request.POST.get('linkedin')
        facebook = request.POST.get('facebook')
        twitter = request.POST.get('twitter')
        insta = request.POST.get('instagram')
        about = request.POST.get('about')
        image = request.FILES.get('image')
        try:
            admin = Author.objects.get(api_token=key)
            if admin is not None:
                # edited attributes
                admin.email = email
                admin.first_name = f_name
                admin.last_name = l_name
                admin.phone_number = phone
                admin.github = github
                admin.linkedin = linkedin
                admin.twitter = twitter
                admin.facebook = facebook
                admin.instagram = insta
                admin.site_title = site_name
                admin.bio = about
                admin.save()
                if image:
                    admin.image = image
                    admin.save()
                return Response({
                    'status': "success",
                    "message": "profile edited successfully",
                    "data": AuthorSerializer(admin).data,
                })
            else:
                return Response({
                    'status': "error",
                    "message": "User not found"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_projects(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        cat_id = self.request.query_params.get('category_id')
        order = self.request.query_params.get('sort_by')
        key = self.request.query_params.get('api_token')
        try:
            admin = Author.objects.get(api_token=key)
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            if order is  None:
                order = 'title'
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = 0
            projects = None
            if cat_id is None:
                total_items = Project.objects.filter(author=admin).filter(
                            Q(title__icontains=query) | Q(description__icontains=query) |
                            Q(live_url__icontains=query) | Q(github_url__icontains=query) |
                            Q(database__title__icontains=query)).count()
                projects = Project.objects.filter(author=admin).filter(
                            Q(title__icontains=query) | Q(description__icontains=query) |
                            Q(live_url__icontains=query) | Q(github_url__icontains=query) |
                            Q(database__title__icontains=query)).order_by(order)[start:stop]
            else:
                cat = ProjectCategory.objects.get(id=int(cat_id))
                total_items = Project.objects.filter(author=admin, category=cat).filter(
                            Q(title__icontains=query) | Q(description__icontains=query) |
                            Q(live_url__icontains=query) | Q(github_url__icontains=query) |
                            Q(database__title__icontains=query)).count()
                projects = Project.objects.filter(author=admin, category=cat).filter(
                            Q(title__icontains=query) | Q(description__icontains=query) |
                            Q(live_url__icontains=query) | Q(github_url__icontains=query) |
                            Q(database__title__icontains=query)).order_by(order)[start:stop]
            total_pages = math.ceil(total_items/per_page)
            if projects.exists():
                return Response({
                    'status': 'success',
                    'data': [ProjectSerializer(pos).data for pos in projects],
                    'message': 'project list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No project found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except Exception as e:
            print(e)
            return Response({
                'status': 'error',
                'message': 'Error getting project list'
            })

    @action(detail=False,
            methods=['get'])
    def get_project(self, request, *args, **kwargs):
        id = self.request.query_params.get('project_id')
        key = self.request.query_params.get('api_token')
        type = self.request.query_params.get('user')
        if id and key:
            try:
                admin = Author.objects.get(api_token=key)
                project = Project.objects.get(id=int(id), author=admin)
                if project is not None:
                    if type is None or type == "client":
                        project.views += 1
                        project.save()
                    elif type == "admin":
                        pass
                    return Response({
                        'status': 'success',
                        'data': ProjectSerializer(project).data,
                        'message': 'project details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid project ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid project ID or API Token'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid project ID or API Token'
            })

    @action(detail=False,
            methods=['post'])
    def create_project(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        db_id = request.POST.get('database_id')
        cat_id = request.POST.get('category_id')
        url = request.POST.get('url')
        github = request.POST.get('github')
        des = request.POST.get('description')
        frames_ids = request.POST.getlist('frame_ids', [])
        image = None
        if request.FILES:
            image = request.FILES.get('image')
        try:
            admin = Author.objects.get(api_token=key)
            if admin is not None:
                # check if position does not exist
                try:
                    project = Project.objects.get(title=title, author=admin)
                    return Response({
                        'status': "error",
                        "message": "project with the same title already exists!"
                    })
                except:
                    category = ProjectCategory.objects.get(id=int(cat_id))
                    database = Database.objects.get(id=int(db_id))
                    new_pro = Project(author=admin, title=title, live_url=url, github_url=github,
                                      description=des, image=image, category=category, database=database)
                    new_pro.save()
                    f_ids = [int(f_id) for f_id in frames_ids]
                    frames = Framework.objects.filter(id__in=f_ids)
                    for f in frames:
                        new_pro.frameworks.add(f)
                        new_pro.save()
                    return Response({
                        'status': "success",
                        "message": "project created sucessfully",
                        "data": ProjectSerializer(new_pro).data,
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except Exception as e:
            print(e)
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

    @action(detail=False,
            methods=['post'])
    def edit_project(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = request.POST.get('project_id')
        title = request.POST.get('title')
        db_id = request.POST.get('database_id')
        cat_id = request.POST.get('category_id')
        url = request.POST.get('url')
        github = request.POST.get('github')
        des = request.POST.get('description')
        frames_ids = request.POST.getlist('frame_ids', [])
        try:
            admin = Author.objects.get(api_token=key)
            if admin is not None:
                try:
                    project = Project.objects.get(id=int(id), author=admin)
                    category = ProjectCategory.objects.get(id=int(cat_id))
                    database = Database.objects.get(id=int(db_id))
                    project.title = title
                    project.category = category
                    project.database = database
                    project.live_url = url
                    project.github_url = github
                    project.description = des
                    project.save()
                    if request.FILES:
                        project.image = request.FILES.get('image')
                        project.save()
                    f_ids = [int(f_id) for f_id in frames_ids]
                    frames = Framework.objects.filter(id__in=f_ids)
                    for f in project.frameworks.all():
                        project.frameworks.remove(f)
                        project.save()
                    for f in frames:
                        project.frameworks.add(f)
                        project.save()
                    return Response({
                        'status': "success",
                        "message": "project edited sucessfully",
                        "data": ProjectSerializer(project).data,
                    })
                except Exception as e:
                    print(e)
                    return Response({
                        "status": "error",
                        "message": f"project with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

    @action(detail=False,
            methods=['post'])
    def delete_project(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = request.POST.get('project_id')
        try:
            admin = Author.objects.get(api_token=key)
            if admin is not None:
                try:
                    project = Project.objects.get(id=int(id), author=admin)
                    project.delete()
                    return Response({
                        'status': "success",
                        "message": f"project \'{project.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"project with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not found"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_comments(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        pro_id = self.request.query_params.get('project_id')
        order = self.request.query_params.get('sort_by')
        key = self.request.query_params.get('api_token')
        try:
            admin = Author.objects.get(api_token=key)
            project = Project.objects.get(id=int(pro_id), author=admin)
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 10
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            if order is  None:
                order = '-date'
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = 0
            total_items = Comment.objects.filter(project=project).filter(
                            Q(name__icontains=query) | Q(email__icontains=query) |
                            Q(comment__icontains=query) | Q(reply__icontains=query)).count()
            comments = Comment.objects.filter(project=project).filter(
                            Q(name__icontains=query) | Q(email__icontains=query) |
                            Q(comment__icontains=query) | Q(reply__icontains=query)).order_by(order)[start:stop]
            total_pages = math.ceil(total_items/per_page)
            if comments.exists():
                return Response({
                    'status': 'success',
                    'project': ProjectSerializer(project).data,
                    'data': [CommentSerializer(pos).data for pos in comments],
                    'message': 'comment list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No comments found',
                    'project': ProjectSerializer(project).data,
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except Exception as e:
            print(e)
            return Response({
                'status': 'error',
                'message': 'Error getting comment list'
            })

    @action(detail=False,
            methods=['get'])
    def get_project(self, request, *args, **kwargs):
        id = self.request.query_params.get('project_id')
        key = self.request.query_params.get('api_token')
        type = self.request.query_params.get('user')
        if id and key:
            try:
                admin = Author.objects.get(api_token=key)
                project = Project.objects.get(id=int(id), author=admin)
                if project is not None:
                    if type is None or type == "client":
                        project.views += 1
                        project.save()
                    elif type == "admin":
                        pass
                    return Response({
                        'status': 'success',
                        'data': ProjectSerializer(project).data,
                        'message': 'project details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid project ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid project ID or API Token'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid project ID or API Token'
            })

    @action(detail=False,
            methods=['post'])
    def create_project(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        db_id = request.POST.get('database_id')
        cat_id = request.POST.get('category_id')
        url = request.POST.get('url')
        github = request.POST.get('github')
        des = request.POST.get('description')
        frames_ids = request.POST.getlist('frame_ids', [])
        image = None
        if request.FILES:
            image = request.FILES.get('image')
        try:
            admin = Author.objects.get(api_token=key)
            if admin is not None:
                # check if position does not exist
                try:
                    project = Project.objects.get(title=title, author=admin)
                    return Response({
                        'status': "error",
                        "message": "project with the same title already exists!"
                    })
                except:
                    category = ProjectCategory.objects.get(id=int(cat_id))
                    database = Database.objects.get(id=int(db_id))
                    new_pro = Project(author=admin, title=title, live_url=url, github_url=github,
                                      description=des, image=image, category=category, database=database)
                    new_pro.save()
                    f_ids = [int(f_id) for f_id in frames_ids]
                    frames = Framework.objects.filter(id__in=f_ids)
                    for f in frames:
                        new_pro.frameworks.add(f)
                        new_pro.save()
                    return Response({
                        'status': "success",
                        "message": "project created sucessfully",
                        "data": ProjectSerializer(new_pro).data,
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except Exception as e:
            print(e)
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

    @action(detail=False,
            methods=['post'])
    def edit_project(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = request.POST.get('project_id')
        title = request.POST.get('title')
        db_id = request.POST.get('database_id')
        cat_id = request.POST.get('category_id')
        url = request.POST.get('url')
        github = request.POST.get('github')
        des = request.POST.get('description')
        frames_ids = request.POST.getlist('frame_ids', [])
        try:
            admin = Author.objects.get(api_token=key)
            if admin is not None:
                try:
                    project = Project.objects.get(id=int(id), author=admin)
                    category = ProjectCategory.objects.get(id=int(cat_id))
                    database = Database.objects.get(id=int(db_id))
                    project.title = title
                    project.category = category
                    project.database = database
                    project.live_url = url
                    project.github_url = github
                    project.description = des
                    project.save()
                    if request.FILES:
                        project.image = request.FILES.get('image')
                        project.save()
                    f_ids = [int(f_id) for f_id in frames_ids]
                    frames = Framework.objects.filter(id__in=f_ids)
                    for f in project.frameworks.all():
                        project.frameworks.remove(f)
                        project.save()
                    for f in frames:
                        project.frameworks.add(f)
                        project.save()
                    return Response({
                        'status': "success",
                        "message": "project edited sucessfully",
                        "data": ProjectSerializer(project).data,
                    })
                except Exception as e:
                    print(e)
                    return Response({
                        "status": "error",
                        "message": f"project with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

    @action(detail=False,
            methods=['post'])
    def delete_project(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = request.POST.get('project_id')
        try:
            admin = Author.objects.get(api_token=key)
            if admin is not None:
                try:
                    project = Project.objects.get(id=int(id), author=admin)
                    project.delete()
                    return Response({
                        'status': "success",
                        "message": f"project \'{project.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"project with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not found"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_new_notifications(self, request, *args, **kwargs):
        key = self.request.query_params.get('api_token')
        try:
            admin = Author.objects.get(api_token=key)
            total_items = Notification.objects.filter(owner=admin, seen=False).count()
            notes = Notification.objects.filter(owner=admin, seen=False)
            if notes.exists():
                return Response({
                    'status': 'success',
                    'data': [NotificationSerializer(pos).data for pos in notes],
                    'message': 'new notifications found',
                    "total_items": total_items,
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No new notifications',
                    "total_items": total_items
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting new notifications'
            })

    @action(detail=False,
            methods=['get'])
    def get_notifications(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        key = self.request.query_params.get('api_token')
        try:
            admin = Author.objects.get(api_token=key)
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Project.objects.filter(author=admin).filter(Q(title__icontains=query) |
                                                                      Q(description__icontains=query)).count()
            total_pages = math.ceil(total_items/per_page)
            projects = Project.objects.filter(author=admin).filter(Q(title__icontains=query) |
                                                                    Q(description__icontains=query))[start:stop]
            if projects.exists():
                return Response({
                    'status': 'success',
                    'data': [ProjectSerializer(pos).data for pos in projects],
                    'message': 'project list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No project found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting project list'
            })

class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_messages(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        key = self.request.query_params.get('api_token')
        try:
            admin = Author.objects.get(api_token=key)
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Contact.objects.filter(owner=admin).filter(Q(name__icontains=query) | Q(email__icontains=query) |
                                                                      Q(message__icontains=query)).count()
            total_pages = math.ceil(total_items/per_page)
            messages = Contact.objects.filter(owner=admin).filter(Q(name__icontains=query) | Q(email__icontains=query) |
                                                                    Q(message__icontains=query))[start:stop]
            pend_mess = Contact.objects.filter(owner=admin, reply="").count()
            if messages.exists():
                return Response({
                    'status': 'success',
                    'data': [ContactSerializer(pos).data for pos in messages],
                    'message': 'message list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "pending_messages": pend_mess,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No message found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "pending_messages": pend_mess,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting message list'
            })

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_categories(self, request, *args, **kwargs):
        try:
            categories = ProjectCategory.objects.all()
            if categories.exists():
                return Response({
                    'status': 'success',
                    'data': [ProjectCategorySerializer(pos).data for pos in categories],
                    'message': 'category list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No category found'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting category list'
            })
    
class FrameworkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Framework.objects.all()
    serializer_class = FrameworkSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_frameworks(self, request, *args, **kwargs):
        try:
            frameworks = Framework.objects.all()
            if frameworks.exists():
                return Response({
                    'status': 'success',
                    'data': [FrameworkSerializer(pos).data for pos in frameworks],
                    'message': 'framework list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No framework found'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting framework list'
            })

class DatabaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_databases(self, request, *args, **kwargs):
        try:
            databases = Database.objects.all()
            if databases.exists():
                return Response({
                    'status': 'success',
                    'data': [DatabaseSerializer(pos).data for pos in databases],
                    'message': 'database list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No database found'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting database list'
            })

class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_skills(self, request, *args, **kwargs):
        key = self.request.query_params.get('api_token')
        try:
            admin = Author.objects.get(api_token=key)
            skills = Skill.objects.filter(owner=admin)
            if skills.exists():
                return Response({
                    'status': 'success',
                    'data': [SkillSerializer(pos).data for pos in skills],
                    'message': 'skills list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No skill found'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting skills list'
            })

