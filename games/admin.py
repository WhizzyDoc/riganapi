from django.contrib import admin
from .models import WordGame, WordCategory

# Register your models here.
@admin.register(WordCategory)
class WordCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created', 'updated']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    
@admin.register(WordGame)
class WordGameAdmin(admin.ModelAdmin):
    list_display = ['word', 'hint', 'category', 'difficulty', 'active', 'created']
    list_filter = ['category', 'difficulty', 'active']
    list_editable = ['hint', 'difficulty', 'active']
    prepopulated_fields = {'meaning': ('hint',)}
    list_per_page = 100