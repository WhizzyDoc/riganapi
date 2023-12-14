from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('users', views.ProfileViewSet)
#router.register('groups', views.GroupViewSet)
#router.register('chatrooms', views.ChatViewSet)
#router.register('notifications', views.NotificationViewSet)
#router.register('gptrooms', views.GPTViewSet)

urlpatterns = [
    path('', include(router.urls)),
]