from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class WordCategory(models.Model):
    title = models.CharField(max_length=100, verbose_name="Title", null=True)
    slug = models.SlugField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = "Word Categories"

DIFFICULTY = (
    ('Easy', 'Easy'),
    ('Medium', 'Medium'),
    ('Hard', 'Hard')
)    
class WordGame(models.Model):
    word = models.CharField(max_length=100, verbose_name="word", null=True)
    hint = models.CharField(max_length=500, verbose_name="hint", null=True)
    meaning = models.TextField(verbose_name="meaning", null=True, blank=True)
    category = models.ForeignKey(WordCategory, on_delete=models.DO_NOTHING, related_name="words")
    active = models.BooleanField(default=False)
    difficulty = models.CharField(max_length=100, verbose_name="Difficulty", choices=DIFFICULTY, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['word']
