from django.urls import path
from .auth_views import csrf_token, current_user, login_view, logout_view

urlpatterns = [
    path("csrf/", csrf_token, name="auth-csrf"),
    path("login/", login_view, name="auth-login"),
    path("me/", current_user, name="auth-me"),
    path("logout/", logout_view, name="auth-logout"),
]
