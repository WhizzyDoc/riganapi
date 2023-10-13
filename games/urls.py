from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('words', views.WordViewSet)
router.register('word-categories', views.WordCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]