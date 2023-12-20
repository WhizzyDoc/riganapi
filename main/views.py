from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import re
import json
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from api.models import App
from blog.models import *

# Create your views here.
def index(request):
    return render(request, 'index.html')

def resume(request, username):
    try:
        user = User.objects.get(username=username)
        admin = Author.objects.get(user=user)
        education = Education.objects.filter(owner=admin)
        skills = Skill.objects.filter(owner=admin)
        experience = Experience.objects.filter(owner=admin)
        interests = Interest.objects.filter(owner=admin)
        projects = Project.objects.filter(author=admin, resume_project=True)
        return render(request, 'resume.html', {
            'admin': admin,
            'education': education,
            'projects': projects,
            'skills': skills,
            'interests': interests,
            'experience':experience,
        })
    except Exception as e:
        print(e)
