from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from tinymce.models import HTMLField

# Create your models here.
class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    first_name = models.CharField(max_length=100, verbose_name="First Name", null=True)
    last_name = models.CharField(max_length=100, verbose_name="Last Name", null=True)
    email = models.EmailField(max_length=200, verbose_name="Email", null=True, blank=True)
    phone_number = models.CharField(max_length=200, verbose_name="Phone Number", null=True, blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True, default="https://instagram.com/")
    site_title = models.CharField(max_length=250, blank=True, null=True)
    bio = HTMLField(blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    work_description = models.TextField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    api_token = models.CharField(max_length=250, verbose_name="API Key", blank=True)
    image = models.ImageField(upload_to="portfolio/author/images/", blank=True)
    site_logo = models.ImageField(upload_to="portfolio/site/images/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.user.__str__()

    class Meta:
        ordering = ['first_name']

class Education(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="education", null=True, blank=True)
    qualification = models.CharField(max_length=250, blank=True)
    grade = models.CharField(max_length=250, blank=True)
    institution = models.CharField(max_length=250, blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    def __str__(self):
        return f'{self.owner.first_name} - {self.institution}'

class Experience(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="experience", null=True, blank=True)
    company = models.CharField(max_length=250, blank=True)
    job_title = models.CharField(max_length=250, blank=True)
    location = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    def __str__(self):
        return f'{self.owner.first_name} - {self.company}'

class Interest(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="interests", null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']

class ProjectCategory(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']

class Skill(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="skills_created", null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="portfolio/skills/images/", blank=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']

class Framework(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']

class Database(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']
    
class Project(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="projects_created", null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    category = models.ForeignKey(ProjectCategory, on_delete=models.DO_NOTHING, related_name="projects", null=True, blank=True)
    database = models.ForeignKey(Database, on_delete=models.DO_NOTHING, related_name="projects", null=True, blank=True)
    frameworks = models.ManyToManyField(Framework, related_name="projects", blank=True)
    short_description = models.TextField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    resume_project = models.BooleanField(default=True)
    views = models.PositiveIntegerField(verbose_name="Views", default=0)
    image = models.ImageField(upload_to="blogs/images/", null=True, blank=True)
    live_url = models.URLField(null=True, blank=True)
    github_url = models.URLField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created']
        
class Resume(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="resume", null=True, blank=True)
    projects = models.ManyToManyField(Project, related_name="resume_in", blank=True)
    skills = models.ManyToManyField(Skill, related_name="skills_in", blank=True)
    description = HTMLField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created']
        
class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    comment = models.TextField()
    reply = models.TextField(blank=True)
    star = models.PositiveIntegerField(verbose_name="Star Rating", default=5)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.comment
    class Meta:
        ordering = ['-date']

class Contact(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="messages")
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    message = models.TextField()
    reply = HTMLField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.message
    class Meta:
        ordering = ['-date']

class Notification(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=150)
    note = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    seen = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-date']