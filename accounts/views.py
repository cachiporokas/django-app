# from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from . import forms

User = get_user_model()

class SignUp(CreateView):
  form_class = forms.CustomUserCreationForm
  success_url = reverse_lazy("login")
  template_name = "accounts/signup.html"


class UserDetail(DetailView):
  model = User
  template_name = 'accounts/account_detail.html'
  context_object_name = "user_detail"

  def get_queryset(self):
    self.user_detail = User.objects.filter(
        id=self.kwargs.get("pk"))
    return self.user_detail


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
  login_url = 'accounts:login'
  template_name = 'accounts/account_form.html'
  form_class = forms.CustomUserChangeForm
  model = User

  def test_func(self):
    return self.request.user.username == self.get_object().username


class UserUpdatePasswordView(PasswordChangeView):
  form_class = PasswordChangeForm
  template_name = 'accounts/change_password.html'
  success_url = reverse_lazy('home')
