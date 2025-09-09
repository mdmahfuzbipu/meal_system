from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.utils.timezone import now

from students.models import Student, DailyMealStatus
from .forms import EmailOrUsernameAuthenticationForm
from .decorators import student_required, manager_required, admin_required
from .models import CustomUser

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


# @admin_required
# def admin_dashboard(request):
#     return render(request, "accounts/admin_dashboard.html")


def is_admin(user):
    role = getattr(user, "role", None)
    return user.is_authenticated and (
        role == "admin" or user.is_staff or user.is_superuser
    )


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    today = now().date()


    total_students = Student.objects.count()

    # Staff count 
    if hasattr(CustomUser, "role"):
        total_staff = CustomUser.objects.filter(
            role__in=["manager", "staff", "admin"]
        ).count()
    else:
        total_staff = CustomUser.objects.filter(is_staff=True).count()

    # Today meal ON counts
    breakfast_on = DailyMealStatus.objects.filter(date=today, breakfast_on=True).count()
    lunch_on = DailyMealStatus.objects.filter(date=today, lunch_on=True).count()
    dinner_on = DailyMealStatus.objects.filter(date=today, dinner_on=True).count()

    context = {
        "page_title": "Admin Dashboard",
        "total_students": total_students,
        "total_staff": total_staff,
        "breakfast_on": breakfast_on,
        "lunch_on": lunch_on,
        "dinner_on": dinner_on,
        "today": today,
    }
    return render(request, "accounts/admin_dashboard.html", context)
