from django.urls import path, include
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.TeamViewList.as_view(template_name='teams/team_list.html'), name='teams_all'),
    path('membership/<username>', views.UserTeamsViewList.as_view(), name='user_teams'),
    path('<slug>/detail/', views.TeamDetailView.as_view(), name = 'team_detail'),
    path('projects/', views.TeamProjectViewList.as_view(), name='projects_all'),
    path('projects/<slug>', views.TeamProjectDetailView.as_view(), name='project_detail'),
    path('projects/by/<username>', views.UserProjectsViewList.as_view(), name='project_user'),
    path('<slug>/posts/', include('message_board.urls', namespace='message_board')),
    path('<slug>/polls/', include('polls.urls', namespace='polls')),
    path('api', views.TeamListAPIView.as_view()),
]



