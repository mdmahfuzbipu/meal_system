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


urlpatterns = [
    path("", role_aware_home, name="home"),
    path("login/", RoleBasedLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("student/dashboard/", student_dashboard, name="student-dashboard"),
    path("manager/dashboard/", manager_dashboard, name="manager-dashboard"),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),
]
