from rest_framework import generics, viewsets
from .models import WordGame, WordCategory
from api.serializers import WordSerializer, WordCategorySerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import action
import re
import json
from django.db.models import Q

# Create your views here.
class WordCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WordCategory.objects.all()
    serializer_class = WordCategorySerializer
    @action(detail=True,
            methods=['get'])
    def get_words(self, request, *args, **kwargs):
        category = self.get_object()
        words = WordGame.objects.filter(category=category)
        return Response({
            'data': [WordSerializer(word).data for word in words]
        })

class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WordGame.objects.all()
    serializer_class = WordSerializer
    @action(detail=False,
            methods=['get'])
    def get_homonyms(self, request, *args, **kwargs):
        word = self.request.query_params.get('word')
        try:
            words = WordGame.objects.filter(word=word)
            return Response({
                'status': 'success',
                'message': 'words found',
                'data': [WordSerializer(word).data for word in words]
            })
        except:
            return Response({
                'status': 'error',
                'message': 'words not found',
            })
    @action(detail=False,
            methods=['get'])
    def word_filter(self, request, *args, **kwargs):
        category = self.request.query_params.get('category')
        difficulty = self.request.query_params.get('difficulty')
        if category and difficulty:
            try:
                category = WordCategory.objects.get(title=category)
                try:
                    words = WordGame.objects.filter(category=category, difficulty=difficulty)
                    return Response({
                        'status': 'success',
                        'message': 'words found',
                        'data': [WordSerializer(word).data for word in words]
                    })
                except:
                    return Response({
                        'status': 'error',
                        'message': 'words not found',
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'category does not exist',
                })
        elif category:
            try:
                category = WordCategory.objects.get(title=category)
                words = WordGame.objects.filter(category=category)
                return Response({
                    'status': 'success',
                    'message': 'words found',
                    'data': [WordSerializer(word).data for word in words]
                })
            except:
                return Response({
                    'status': 'error',
                    'message': 'category does not exist',
                })
        elif difficulty:
            try:
                words = WordGame.objects.filter(category=category, difficulty=difficulty)
                return Response({
                    'status': 'success',
                    'message': 'words found',
                    'data': [WordSerializer(word).data for word in words]
                })
            except:
                return Response({
                    'status': 'error',
                    'message': 'words not found',
                })
