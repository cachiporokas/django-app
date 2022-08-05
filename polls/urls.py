from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    # path('by/<username>'),
    path('new/', views.CreatePollView.as_view(), name='create_poll'),
    path('add_choices/<int:pk>', views.PollAddChoicesView.as_view(), name='poll_add_choices'),
    path('detail/<int:pk>', views.PollDetailView.as_view(), name='poll_detail')
]
