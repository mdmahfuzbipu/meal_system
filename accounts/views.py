from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from .forms import EmailOrUsernameAuthenticationForm
from .decorators import student_required, manager_required, admin_required


import logging

logger = logging.getLogger(__name__)

# Create your views here.

class RoleBasedLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailOrUsernameAuthenticationForm

    def get_success_url(self):
        user = self.request.user
        if user.role == "student":
            return reverse_lazy("home")
        elif user.role == "manager":
            return reverse_lazy("home")
        elif user.is_superuser or user.role == "admin":
            return reverse_lazy("home")
        logger.warning(f"User {user.username} has unknown role: {user.role}")
        return reverse_lazy("login")

@login_required
def role_aware_home(request):
    return render(request, "accounts/home.html")


@student_required
def student_dashboard(request):
    return render(request, "accounts/student_dashboard.html", context={"page_title": "Student Dashboard"})


@manager_required
def manager_dashboard(request):
    return render(request, "accounts/manager_dashboard.html")


@admin_required
def admin_dashboard(request):
    return render(request, "accounts/admin_dashboard.html")
