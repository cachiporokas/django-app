from click import option
from django import template
import misaka
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from teams.models import Team

# Create your models here.
register = template.Library()
User = get_user_model()


class Poll(models.Model):
  title = models.CharField(max_length=200)
  creation_date = models.DateTimeField(auto_now_add=True)
  update_date = models.DateTimeField(auto_now=True)
  description = models.CharField(max_length=600)
  description_html = models.TextField(editable=False)
  active = models.BooleanField(default=False)
  team = models.ForeignKey(
      Team, related_name='team_poll', on_delete=models.CASCADE)
  user = models.ManyToManyField(User, related_name='polls')

  class Meta():
    ordering = ['-creation_date']

  def __str__(self):
    return self.title

  def save(self, *args, **kwargs):
    self.description_html = misaka.html(self.description)
    super().save(*args, **kwargs)

  def get_absolute_url(self):
    return reverse('teams:polls:poll_add_choices', kwargs={"slug": self.team.slug, "pk": self.pk})

  def description_snip(self):
    return self.description[:50] + ' ...'

  def publication_type(self):
    return 'poll'


class Choice(models.Model):
  option = models.CharField(max_length=100)
  votes = models.IntegerField(default=0)
  poll = models.ForeignKey(
      Poll, related_name='choices', on_delete=models.CASCADE)

  def __str__(self):
    return self.option
