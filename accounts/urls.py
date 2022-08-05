from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('users/update/<int:pk>/', views.UserUpdateView.as_view(), name='user_update'),
    # path('users/update/password/<int:pk>', auth_views.PasswordChangeView.as_view(
        # template_name='accounts/change_password.html'), name='user_change_password'),
    path('users/update/password/', views.UserUpdatePasswordView.as_view(), name='user_update')
]
