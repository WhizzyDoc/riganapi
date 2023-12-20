from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('resume/<str:username>/', views.resume, name="resume"),
]