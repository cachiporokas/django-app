from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.urls import reverse

from . managers import CustomUserManager

# Create your models here.


def get_upload_path(instance, filename):
  return f"accounts/user_{instance.id}/{filename}"


class CustomUser(AbstractUser):
  first_name = models.CharField(max_length=150)
  last_name = models.CharField(max_length=150)
  email = models.EmailField(_('email address'), unique=True)
  profile_image = models.ImageField(
      null=True, blank=True, upload_to=get_upload_path)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ('username',)

  objects = CustomUserManager()

  def __str__(self):
    return self.email

  def get_absolute_url(self):
    return reverse("accounts:user_detail", kwargs={"pk": self.pk})
