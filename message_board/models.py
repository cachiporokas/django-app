from enum import unique
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import template
# import misaka
from django.utils.text import slugify
from teams.models import Team

# Create your models here.
register = template.Library
User = get_user_model()


class Publication(models.Model):
  POST = 'post'
  POLL = 'poll'
  PUBLICATION_TYPE = [
      (POST, 'Normal Publication'),
      (POLL, 'Publication with poll'),
  ]

  title = models.CharField(max_length=150)
  slug = models.SlugField(allow_unicode=True, unique=True)
  message = models.TextField(null=False)
  # message_html = models.TextField(editable=False)
  creation_date = models.DateTimeField(auto_now_add=True)
  update_date = models.DateTimeField(auto_now=True)
  is_active = models.BooleanField(default=False)
  author = models.ForeignKey(User, related_name='posts',
                             on_delete=models.RESTRICT)
  team = models.ForeignKey(
      Team, related_name='team_post', on_delete=models.CASCADE)

  category = models.CharField(
      max_length=20,
      choices=PUBLICATION_TYPE,
      default=POST,
  )

  class Meta():
    ordering = ['-creation_date']

  def __str__(self):
    return self.title

  def message_snip(self):
    return self.message[:50] + ' ...'

  def save(self, *args, **kwargs):
    self.slug = slugify(self.title)
    # self.message_html = misaka.html(self.message)
    super().save(*args, **kwargs)

  def get_replies(self):
    return self.comments.all()

  def get_allowed_users(self):
    return self.team.members.all()


class Comment(models.Model):
  message = models.TextField(null=False)
  message_html = models.TextField(editable=False)
  creation_date = models.DateTimeField(auto_now_add=True)
  update_date = models.DateTimeField(auto_now=True)
  # nesting_level = models.IntegerField()
  parent = models.ForeignKey(
      'self', related_name='childs', null=True, blank=True, on_delete=models.CASCADE)
  author = models.ForeignKey(
      User, related_name='comments', on_delete=models.CASCADE)
  post = models.ForeignKey(
      Publication, related_name='comments', on_delete=models.CASCADE)

  class Meta():
    ordering = ['-creation_date']

  def __str__(self):
    return self.message

  # def get_absolute_url(self):
  #   return reverse("teams:message_board:post_detail", kwargs={"slug": self.post.team.slug, "pk": self.post.id})

  def save(self, *args, **kwargs):
    # self.message_html = misaka.html(self.message)
    if not self.parent:
      self.parent = None
      # self.nesting_level = 0
    super().save(*args, **kwargs)


class PollOption(models.Model):
  is_cleaned = False
  option = models.CharField(max_length=150, null=False)
  votes = models.IntegerField(default=0)
  publication = models.ForeignKey(
      Publication, related_name='poll_options', on_delete=models.CASCADE)
  voters = models.ManyToManyField(User, 
                                  blank=True, 
                                  related_name='selected_option', 
                                  through='Vote',
                                  through_fields=('poll_option', 'user'))

  def __str__(self):
    return self.option

  def clean(self):
    if hasattr(self, 'publication') and self.publication.category != 'poll':
      raise ValidationError(
          'Only publications of type "Poll" can have options')
    self.is_cleaned = True

  def save(self, *args, **kwargs):
    if not self.is_cleaned:
      self.clean()
    super(PollOption, self).save(*args, **kwargs)
  
class Vote(models.Model):
  poll_option = models.ForeignKey(PollOption, on_delete=models.DO_NOTHING)
  user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
  publication = models.ForeignKey(Publication, on_delete=models.DO_NOTHING)
  
  class Meta():
    constraints = [
                   models.UniqueConstraint(fields=['user', 'publication'], name='unique_vote')
                   ]

  def clean(self):
    if self.poll_option.publication != self.publication:
      raise ValidationError(
        'Option does not belong to the poll'
      )
    
  def save(self, *args, **kwargs):
    self.clean()
    super(Vote, self).save(*args, **kwargs)