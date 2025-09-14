from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.contrib import messages

from managers.models import WeeklyMenuProposal
from students.models import Student, WeeklyMenu
from accounts.models import CustomUser
from .forms import StudentRegistrationForm

def is_admin(user):
    role = getattr(user, "role", None)
    return user.is_authenticated and (
        role == "admin" or user.is_staff or user.is_superuser
    )


@login_required
@user_passes_test(is_admin)
def manage_students(request):
    return render(request, "admins/manage_students.html")


@login_required
@user_passes_test(is_admin)
def manage_staff(request):
    return render(request, "admins/manage_staff.html")


@login_required
@user_passes_test(is_admin)
def approvals(request):
    return render(request, "admins/approvals.html")


@login_required
@user_passes_test(is_admin)
def weekly_menu(request):
    return render(request, "admins/weekly_menu.html")


@login_required
@user_passes_test(is_admin)
def meal_costs(request):
    return render(request, "admins/meal_costs.html")


@login_required
@user_passes_test(is_admin)
def analytics(request):
    return render(request, "admins/analytics.html")


@login_required
@user_passes_test(is_admin)
@login_required
def manage_students(request):
    # Search
    query = request.GET.get("q", "")
    students = Student.objects.select_related("user").all()
    if query:
        students = students.filter(user__full_name__icontains=query)  # or username/roll

    # Pagination
    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    students_page = paginator.get_page(page_number)

    # Add New Student
    if request.method == "POST":
        name = request.POST.get("name")
        username = request.POST.get("username")
        password = request.POST.get("password")
        roll = request.POST.get("roll")
        room = request.POST.get("room")
        phone = request.POST.get("phone")

        # Validate
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        else:
            user = CustomUser.objects.create_user(
                username=username, password=password, role="student"
            )
            Student.objects.create(user=user, roll=roll, room_number=room, phone=phone)
            messages.success(request, f"Student {name} added successfully!")
            return redirect("manage-students")

    return render(
        request,
        "admins/manage_students.html",
        {"students": students_page, "query": query},
    )


@login_required
@user_passes_test(is_admin)
def admin_menu_list(request):
    proposals = WeeklyMenuProposal.objects.filter(status="pending")
    return render(request, "admins/admin_menu_list.html", {"proposals": proposals})


@login_required
@user_passes_test(is_admin)
def approve_menu(request, proposal_id):
    proposal = get_object_or_404(WeeklyMenuProposal, id=proposal_id)
    proposal.status = "approved"
    proposal.save()

    # Copy to students.models.WeeklyMenu
    WeeklyMenu.objects.update_or_create(
        day_of_week=proposal.day_of_week,
        defaults={
            "breakfast_main": proposal.breakfast_main,
            "breakfast_cost": proposal.breakfast_cost,
            "lunch_main": proposal.lunch_main,
            "lunch_cost": proposal.lunch_cost,
            "lunch_contains_beef": proposal.lunch_contains_beef,
            "lunch_contains_fish": proposal.lunch_contains_fish,
            "dinner_main": proposal.dinner_main,
            "dinner_cost": proposal.dinner_cost,
            "dinner_contains_beef": proposal.dinner_contains_beef,
            "dinner_contains_fish": proposal.dinner_contains_fish,
        },
    )

    messages.success(request, "Menu approved and copied to final menu!")
    return redirect("admin_menu_list")


@login_required
@user_passes_test(is_admin)
def reject_menu(request, proposal_id):
    proposal = get_object_or_404(WeeklyMenuProposal, id=proposal_id)
    proposal.status = "rejected"
    proposal.save()
    messages.error(request, "Menu proposal rejected.")
    return redirect("admin_menu_list")


def is_superuser(user):
    return user.is_active and user.is_superuser


@user_passes_test(is_superuser)
def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student account created successfully.")
            return redirect("admins:register_student")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = StudentRegistrationForm()
    return render(
        request,
        "admins/register_student.html",
        {
            "form": form,
            "page_title": "Register New Student",
        },
    )
