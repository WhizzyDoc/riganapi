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

# Create your views here.
def index(request):
    return render(request, 'index.html')
