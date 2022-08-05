from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.detail import SingleObjectMixin
from braces.views import SelectRelatedMixin
from django.http import Http404, HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib import messages


from .models import Poll, Choice
from .forms import PollChoiceFormset
from teams.models import Team

# Create your views here.

User = get_user_model()

class PollDetailView(generic.DetailView):
   model = Poll
   template_name = 'polls/poll_detail.html'

class CreatePollView(LoginRequiredMixin, 
                 UserPassesTestMixin, 
                 SelectRelatedMixin, 
                 generic.CreateView):
   model = Poll
   fields = ['title', 'description', 'active']
   template_name = 'polls/poll_create.html'
   
   def form_valid(self, form):
      self.object = form.save(commit=False)
      self.object.team = Team.objects.get(slug=self.kwargs.get('slug'))
      return super().form_valid(form)
    
   def test_func(self):
      current_team = self.kwargs.get('slug')
      return self.request.user.teams.filter(slug=current_team).exists()

class PollAddChoicesView(SingleObjectMixin, generic.FormView):
   model = Choice
   template_name = 'polls/poll_edit_choices.html'
   
   def get(self, request, *args, **kwargs):
      self.object = self.get_object(queryset=Poll.objects.all())
      return super().get(request, *args, **kwargs)
   
   def post(self, request, *args, **kwargs):
      self.object = self.get_object(queryset=Poll.objects.all())
      return super().post(request, *args, **kwargs)
   
   def get_form(self, form_class=None):
      return PollChoiceFormset(**self.get_form_kwargs(), instance=self.object)
   
   def form_valid(self, form):
      form.save()
      
      messages.add_message(
         self.request,
         messages.SUCCESS,
         'Poll saved'
      )
      
      return HttpResponseRedirect(self.get_success_url())
   
   def get_success_url(self):
      return reverse('teams:polls:poll_detail', kwargs={"slug": self.kwargs.get("slug"), "pk": self.kwargs.get("pk")})