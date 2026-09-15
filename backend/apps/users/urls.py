"""Authentication endpoints (users app)."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users import views

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="auth-register"),
    path("login", views.LoginView.as_view(), name="auth-login"),
    path("refresh", TokenRefreshView.as_view(), name="auth-refresh"),
    path("logout", views.LogoutView.as_view(), name="auth-logout"),
    path("me", views.MeView.as_view(), name="auth-me"),
    path("forgot-password", views.ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("reset-password", views.ResetPasswordView.as_view(), name="auth-reset-password"),
]