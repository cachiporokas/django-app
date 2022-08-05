from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import template
import misaka
from django.utils.text import slugify


# Create your models here.
register = template.Library()
User = get_user_model()

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField(blank=True, default='')
    description_html = models.TextField(editable=False, default='', blank=True)
    manager = models.ForeignKey(User, related_name='managed_teams', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='teams')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.description_html = misaka.html(self.description)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('teams:team_detail', kwargs={'slug': self.slug})
    
    class Meta():
        ordering = ['name']
        
    
class TeamProject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField(blank=True, default='')
    description_html = models.TextField(editable=False, default='', blank=True)
    active = models.BooleanField(default=False)
    teams = models.ManyToManyField(Team, related_name='projects')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.description_html = misaka.html(self.description)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('teams:single2', kwargs={'slug': self.slug})
    
    class Meta():
        ordering = ['name']