from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('author', views.AuthorViewSet)
router.register('projects', views.ProjectViewSet)
router.register('messages', views.ContactViewSet)
router.register('notifications', views.NotificationViewSet)
router.register('categories', views.CategoryViewSet)
router.register('frameworks', views.FrameworkViewSet)
router.register('databases', views.DatabaseViewSet)
router.register('comments', views.CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]