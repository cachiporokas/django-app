from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from . models import CustomUser


class CustomUserCreationForm(UserCreationForm):
  first_name = forms.CharField(max_length=150, help_text='150 characters max.')
  last_name = forms.CharField(max_length=150, help_text='150 characters max.')
  email = forms.EmailField(max_length=100, help_text='100 characters max.')
  username = forms.CharField(
      max_length=100, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
  profile_image = forms.ImageField(
      help_text='You may continue without selecting a profile image.', required=False)

  class Meta:
    model = CustomUser
    fields = ('email', 'username', 'profile_image')


class CustomUserChangeForm(UserChangeForm):

  class Meta:
    model = CustomUser
    fields = ('email', 'username', 'profile_image')
