from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction

from managers.models import WeeklyMenuProposal
from students.models import Student, WeeklyMenu, StudentDetails
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
def manage_students(request):

    query = request.GET.get("q", "")
    students = Student.objects.select_related("user").all()
    if query:
        students = students.filter(user__full_name__icontains=query)  # or username/roll

    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    students_page = paginator.get_page(page_number)

    if request.method == "POST":
        name = request.POST.get("name")
        username = request.POST.get("username")
        password = request.POST.get("password")
        roll = request.POST.get("roll")
        room = request.POST.get("room")
        phone = request.POST.get("phone")

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
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    details = getattr(student, "studentdetails", None)

    if request.method == "POST":
        # Student basic info
        student.name = request.POST.get("name")
        student.room_number = request.POST.get("room")
        student.save()

        # StudentDetails fields
        roll = request.POST.get("roll")
        dept = request.POST.get("department")
        batch = request.POST.get("batch")
        dob = request.POST.get("dob")
        nid = request.POST.get("nid")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        blood = request.POST.get("blood_group")
        guardian_name = request.POST.get("guardian_name")
        guardian_phone = request.POST.get("guardian_phone")
        profile_pic = request.FILES.get("profile_picture")

        if details:
            details.university_id = roll
            details.department = dept
            details.batch = batch
            details.date_of_birth = dob
            details.national_id = nid
            details.address = address
            details.phone_number = phone
            details.blood_group = blood
            details.guardian_name = guardian_name
            details.guardian_phone = guardian_phone
            if profile_pic:
                details.profile_picture = profile_pic
            details.save()
        else:
            StudentDetails.objects.create(
                student=student,
                university_id=roll,
                department=dept,
                batch=batch,
                date_of_birth=dob,
                national_id=nid,
                address=address,
                phone_number=phone,
                blood_group=blood,
                guardian_name=guardian_name,
                guardian_phone=guardian_phone,
                profile_picture=profile_pic,
            )

        messages.success(request, "Student information updated successfully!")
        return redirect("admins:manage_students")

    return render(
        request, "admins/edit_student.html", {"student": student, "details": details}
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


@login_required
@user_passes_test(lambda u: u.role == "admin")
@transaction.atomic
def review_weekly_proposals(request):
    # Get all available week start dates (distinct)
    weeks = (
        WeeklyMenuProposal.objects.order_by("-week_start_date")
        .values_list("week_start_date", flat=True)
        .distinct()
    )

    # Get selected week from dropdown default:latest
    selected_week = request.GET.get("week")
    if not selected_week and weeks:
        selected_week = weeks[0].strftime("%Y-%m-%d")

  
    proposals = WeeklyMenuProposal.objects.filter(
        status="pending", week_start_date=selected_week
    ).order_by("day_of_week")

    # Handle Approve/Reject
    if request.method == "POST":
        proposal_id = request.POST.get("proposal_id")
        action = request.POST.get("action")
        proposal = WeeklyMenuProposal.objects.get(id=proposal_id)

        if action == "approve":
            weekly_menu, created = WeeklyMenu.objects.update_or_create(
                day_of_week=proposal.day_of_week,
                defaults={
                    "breakfast_main": proposal.breakfast_main,
                    "breakfast_cost": proposal.breakfast_cost,
                    "lunch_main": proposal.lunch_main,
                    "lunch_cost": proposal.lunch_cost,
                    "lunch_contains_beef": proposal.lunch_contains_beef,
                    "lunch_contains_fish": proposal.lunch_contains_fish,
                    "lunch_alternate": proposal.lunch_alternate,
                    "lunch_cost_alternate": proposal.lunch_cost_alternate,
                    "dinner_main": proposal.dinner_main,
                    "dinner_cost": proposal.dinner_cost,
                    "dinner_contains_beef": proposal.dinner_contains_beef,
                    "dinner_contains_fish": proposal.dinner_contains_fish,
                    "dinner_alternate": proposal.dinner_alternate,
                    "dinner_cost_alternate": proposal.dinner_cost_alternate,
                },
            )
            proposal.status = "approved"
            proposal.linked_menu = weekly_menu
            proposal.save()
            messages.success(request, f"✅ Approved {proposal.day_of_week}.")
        elif action == "reject":
            proposal.status = "rejected"
            proposal.save()
            messages.warning(
                request, f"❌ Rejected proposal for {proposal.day_of_week}."
            )

        return redirect(f"{request.path}?week={selected_week}")

    return render(
        request,
        "admins/review_weekly_proposals.html",
        {"proposals": proposals, "weeks": weeks, "selected_week": selected_week},
    )
