from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.contrib import messages

from meal_system import settings
from managers.models import SpecialMealRequest
from students.models import Student, DailyMealStatus
from .forms import EmailOrUsernameAuthenticationForm
from .decorators import student_required, manager_required, admin_required
from .models import CustomUser
from notices.utils import get_unread_notice_count
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
        return reverse_lazy("accounts:login")

@login_required
def role_aware_home(request):
    unread_notices = get_unread_notice_count(request.user)
    return render(request, "accounts/home.html", {"unread_notices": unread_notices})


@student_required
def student_dashboard(request):
    return render(request, "accounts/student_dashboard.html", context={"page_title": "Student Dashboard"})


@manager_required
def manager_dashboard(request):
    # Get pending special meal requests for this manager
    pending_requests = SpecialMealRequest.objects.filter(
        manager=request.user, status=SpecialMealRequest.STATUS_PENDING
    )
    pending_count = pending_requests.count()

    return render(
        request,
        "accounts/manager_dashboard.html",
        {
            "pending_requests": pending_requests,
            "pending_count": pending_count,
            "page_title": "Manager Dashboard",
        },
    )

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


from django.contrib.auth.views import PasswordResetView


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    template_name = "accounts/password_reset.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_year"] = settings.CURRENT_YEAR
        return context
