# urls.py
from django.urls import path
from .views.auth import views
from .views import dashboard

app_name = 'auth'

urlpatterns = [
    path('api/sign-up', views.signup, name='api_signup'),
    path('api/verify-status', views.verify_status, name='api_verify_status'),
    path('api/verify-account', views.verify_account, name='api_verify_account'),
    path('api/sign-in', views.signin, name='api_signin'),
    path('api/send-code-to-mail', views.send_code_to_mail, name='api_send_code'),
    path('api/verify-code', views.verify_code, name='api_verify_code'),
    path('api/reset-password', views.reset_password, name='api_reset_password'),
    path('api/refresh-token', views.refresh_token, name='api_refresh_token'),
    path('api/validate-session', views.validate_session, name='api_validate_session'),
    path('api/get-current-user', views.get_current_user, name='api_get_current_user'),
    path('api/sign-out', views.signout, name='api_signout'),
    
    path('sign-in', views.signin_page, name='signin_page'),
    path('sign-up', views.signup_page, name='signup_page'),
    path('forgot-password', views.forgot_password_page, name='forgot_password_page'),
    path('reset-password', views.reset_password_page, name='reset_password_page'),
    path('verify-account', views.verify_account_page, name='verify_account_page'),

    path('dashboard', dashboard.dashboard_render, name='dashboard'),
]