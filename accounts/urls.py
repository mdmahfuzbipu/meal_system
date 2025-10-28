from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CustomPasswordResetView,
    role_aware_home, 
    RoleBasedLoginView,
    student_dashboard,
    manager_dashboard,
    admin_dashboard,
    )
from . import views

app_name = "accounts"

urlpatterns = [
    path("", role_aware_home, name="home"),
    path("login/", RoleBasedLoginView.as_view(), name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="accounts:login"),
        name="logout",
    ),
    # Password reset
    path(
        "password-reset/",
        CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path("manager-dashboard/", manager_dashboard, name="manager_dashboard"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
]
