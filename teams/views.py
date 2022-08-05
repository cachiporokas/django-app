from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse
from django.views import generic

from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from . import models
from teams import serializers

User = get_user_model()

# Create your views here.


class TeamViewList(generic.ListView):
  model = models.Team
  template_name = 'teams/team_list.html'


class TeamDetailView(generic.DetailView):
  model = models.Team

  def get_queryset(self):
    queryset = super().get_queryset()
    try:
      return queryset.filter(slug=self.kwargs.get("slug"))
    except models.Team.DoesNotExist:
      raise Http404


class TeamProjectViewList(generic.ListView):
  model = models.TeamProject
  template_name = 'teams/project_list.html'
  context_object_name = 'project_list'


class UserTeamsViewList(generic.ListView):
  model = models.Team
  template_name = 'teams/user_team_list.html'

  def get_queryset(self):
    try:
      self.teams_user = User.objects.prefetch_related(
          'teams').get(username__iexact=self.kwargs.get('username'))
    except User.DoesNotExist:
      raise Http404
    else:
      return self.teams_user.teams.all()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["team_user"] = self.teams_user
    return context


class UserProjectsViewList(generic.ListView):
  model = models.TeamProject
  template_name = 'teams/project_list.html'

  def get_queryset(self):
    try:
      self.teams_user = User.objects.prefetch_related(
          'teams').get(username__iexact=self.kwargs.get('username'))
      self.projects_user = models.TeamProject.objects.filter(
          teams__in=self.teams_user.teams.all())
    except User.DoesNotExist:
      raise Http404
    else:
      return self.projects_user

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["project_list"] = self.projects_user.distinct()
    context["subset"] = 'True'
    return context


class TeamProjectDetailView(generic.DetailView):
  model = models.TeamProject
  template_name = 'teams/project_detail.html'

  def get_queryset(self):
    queryset = super().get_queryset()
    try:
      return queryset.filter(slug=self.kwargs.get("slug"))
    except models.TeamProject.DoesNotExist:
      raise Http404


class TeamListAPIView(generics.ListAPIView):
  queryset = models.Team.objects.all()
  serializer_class = serializers.TeamSerializer
  permission_classes = [permissions.IsAuthenticated]
  renderer_classes = [JSONRenderer]

  # def get(self, request, *args, **kwargs):
  #   teams = models.Team.objects.all()
  #   serializer = TeamSerializer
  #   return Response(serializer.data, status=status.HTTP_200_OK)
