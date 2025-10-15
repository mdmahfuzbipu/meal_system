from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
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
    path("logout/", auth_views.LogoutView.as_view(next_page="accounts:login"), name="logout"),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path("manager-dashboard/", manager_dashboard, name="manager_dashboard"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
]
