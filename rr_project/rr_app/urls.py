from django.urls import path
from .views import auth

urlpatterns = [
    path('login/', auth.login_render, name='login'),  # Keep this if you want the old URL
    path('register/', auth.register_render, name ='register'),
    path('reset_password/', auth.reset_password_render, name = 'reset_password'),
    path('forgot_password/', auth.forgot_pass_render, name ='forgot_password'),
    path('register_user/', auth.register_user, name ='register_user'),
    path('login_user/', auth.login_user, name ='login_user'),
    path('fpass_request/', auth.fpass_request, name ='fpass_request'),
    path('reset_passsword', auth.reset_password_request, name='reset_password'),
    path('refresh_token', auth.refresh_token, name='refresh_token'),
]