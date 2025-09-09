from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.contrib import messages

from students.models import Student
from accounts.models import CustomUser


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
