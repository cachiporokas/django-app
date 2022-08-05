from django.urls import path
from . import views

app_name = 'message_board'

urlpatterns = [
  ## Post
  path('', views.PostList.as_view(), name='team_posts'),
  path('my_drafts/<str:drafts>', views.PostList.as_view(), name='user_drafts'),
  path('new/', views.CreatePost.as_view(), name='create_post'),
  path('by/<username>/', views.UserPostList.as_view(), name='user_post'),
  path('detail/<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
  path('update/<int:pk>/', views.UpdatePost.as_view(), name='update_post'),
  path('delete/<int:pk>/', views.DeletePost.as_view(), name='delete_post'),
  ## Comments and replies
  path('newComment/<int:pk>/', views.CreateCommentView.as_view(), name='create_comment'),
  path('comment_detail/<int:pk>/', views.CommentDetailView.as_view(), name='comment_detail'),
  path('<int:pk>/publication_comments/<str:parent_pk>/', views.CommentListView.as_view(), name='comment_list'),
  path('newReply/<int:pk>/<int:parent_pk>/', views.CreateReplyToCommentView.as_view(), name='create_reply'),
  ## Poll and votes
  path('<int:pk>/add_option/', views.PollOptionCreateView.as_view(), name='add_poll_option'),
  path('<int:pub_pk>/poll_option_detail/<int:pk>/', views.PollOptionDetailView.as_view(), name="poll_option_detail"),
  path('<int:pub_pk>/poll_option_list/', views.PollOptionListView.as_view(), name="poll_option_list"), 
  path('<int:pub_pk>/update_option/<int:pk>/', views.PollOptionUpdateView.as_view(), name="update_poll_option"),
  path('<int:pub_pk>/delete_option/<int:pk>/', views.PollOptionDeleteView.as_view(), name="delete_poll_option"),
  path('<int:pub_pk>/poll_vote/<int:pk>/<action>/', views.vote, name="poll_vote"),
]
