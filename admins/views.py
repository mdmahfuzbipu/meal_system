from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.contrib.auth import get_user_model

from admins.models import AdminProfile
from managers.forms import ManagerRegistrationForm
from managers.models import ManagerProfile, SpecialMealRequest, WeeklyMenuProposal
from students.models import PaymentSlip, Student, WeeklyMenu, StudentDetails, Complaint
from accounts.models import CustomUser
from accounts.decorators import admin_required
from .forms import StudentRegistrationForm

User = get_user_model()


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

@admin_required
def register_manager(request):
    if request.method == "POST":
        form = ManagerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Manager registered successfully!")
            return redirect("admins:register_manager")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ManagerRegistrationForm()

    return render(request, "admins/register_manager.html", {"form": form})


@admin_required
def manage_managers(request):
    managers = ManagerProfile.objects.select_related("user").order_by("-created_at")
    return render(request, "admins/manage_managers.html", {"managers": managers})


@admin_required
def edit_manager(request, manager_id):
    manager = get_object_or_404(ManagerProfile, id=manager_id)
    if request.method == "POST":
        form = ManagerRegistrationForm(request.POST, request.FILES, instance=manager)
        if form.is_valid():
            form.save()
            messages.success(request, "Manager information updated successfully.")
            return redirect("admins:manage_managers")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial_data = {
            "username": manager.user.username,
            "email": manager.user.email,
            "full_name": manager.full_name,
        }
        form = ManagerRegistrationForm(instance=manager, initial=initial_data)

    return render(
        request, "admins/edit_manager.html", {"form": form, "manager": manager}
    )


@login_required
@user_passes_test(is_admin)
def toggle_manager_status(request, manager_id):
    manager = get_object_or_404(ManagerProfile, id=manager_id)
    user = manager.user

    user.is_active = not user.is_active 
    user.save()

    if user.is_active:
        messages.success(request, f"Manager '{manager.full_name}' has been activated.")
    else:
        messages.warning(
            request, f"Manager '{manager.full_name}' has been deactivated."
        )

    return redirect("admins:manage_managers")


@login_required
@user_passes_test(is_admin)
def manage_students(request):

    query = request.GET.get("q", "")
    students = Student.objects.select_related("user").all()
    if query:
        students = students.filter(
            Q(name__icontains=query)
            | Q(user__username__icontains=query)
            | Q(room_number__icontains=query)
        )
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
        {
            "students": students_page,
            "query": query,
            "page_title": "Manage Students",
        },
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
def toggle_student_status(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    user = student.user

    user.is_active = not user.is_active
    user.save()

    if user.is_active:
        messages.success(request, f"Student '{student.name}' has been activated.")
    else:
        messages.warning(request, f"Student '{student.name}' has been deactivated.")

    return redirect("admins:manage_students")


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


@admin_required
def view_complaints(request):
    complaints = Complaint.objects.all().order_by("-created_at")
    return render(
        request,
        "admins/view_complaints.html",
        {
            "complaints": complaints,
            "page_title": "View Complaints",
        },
    )


@login_required
def profile_view(request):
    """Display the logged-in admin’s profile information"""
    admin_profile = get_object_or_404(AdminProfile, user=request.user)

    context = {
        "page_title": "My Profile",
        "admin_profile": admin_profile,
    }
    return render(request, "admins/profile.html", context)


def is_super_admin(user):
    return user.is_superuser

from django.contrib.auth.hashers import make_password


@login_required
@user_passes_test(is_super_admin)
def register_admin(request):
    """Register a new admin and redirect to Manage Admins"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")
        employee_id = request.POST.get("employee_id")
        user_type = request.POST.get("user_type", "teacher")
        designation = request.POST.get("designation")
        hall_role = request.POST.get("hall_role")
        department = request.POST.get("department")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        assigned_floor = request.POST.get("assigned_floor")
        photo = request.FILES.get("photo")

        # Basic validation
        if not username or not password or not name or not employee_id:
            messages.error(request, "Please fill required fields.")
            return redirect("admins:register_admin")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Choose another.")
            return redirect("admins:register_admin")

        if AdminProfile.objects.filter(employee_id=employee_id).exists():
            messages.error(request, "Employee ID already registered.")
            return redirect("admins:register_admin")

        try:
            with transaction.atomic():
                # Use create_user to handle password hashing and any custom user logic
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    is_active=True,
                    role="admin",  # set role explicitly
                )

                AdminProfile.objects.create(
                    user=user,
                    name=name,
                    employee_id=employee_id,
                    user_type=user_type,
                    designation=designation,
                    hall_role=hall_role,
                    department=department,
                    phone=phone,
                    email=email,
                    assigned_floor=assigned_floor,
                    photo=photo,
                )

            messages.success(request, f"Admin '{name}' registered successfully!")
            return redirect("admins:manage_admins")

        except IntegrityError:
            messages.error(request, "Database error during registration. Try again.")
            return redirect("admins:register_admin")

    context = {
        "DESIGNATION_CHOICES": AdminProfile.DESIGNATION_CHOICES,
        "HALL_ROLE_CHOICES": AdminProfile.HALL_ROLE_CHOICES,
    }
    return render(request, "admins/register_admin.html", context)


# ---------------- Manage Admins ----------------
@login_required
@user_passes_test(is_super_admin)
def manage_admins(request):
    """Display a list of all admins."""
    admins = AdminProfile.objects.all().order_by("name")
    return render(
        request,
        "admins/manage_admins.html",
        {
            "admins": admins,
            "page_title": "Manage Admin",
        },
    )


# ---------------- Edit Admin ----------------
@login_required
@user_passes_test(is_super_admin)
def edit_admin(request, admin_id):
    admin_profile = get_object_or_404(AdminProfile, id=admin_id)

    if request.method == "POST":
        admin_profile.name = request.POST.get("name")
        admin_profile.employee_id = request.POST.get("employee_id")
        admin_profile.department = request.POST.get("department")
        admin_profile.designation = request.POST.get("designation")
        admin_profile.hall_role = request.POST.get("hall_role")
        admin_profile.hall_responsibilities = request.POST.get("hall_responsibilities")
        admin_profile.assigned_floor = request.POST.get("assigned_floor")
        admin_profile.phone = request.POST.get("phone")
        admin_profile.email = request.POST.get("email")

        # handle uploaded photo
        photo = request.FILES.get("photo")
        if photo:
            admin_profile.photo = photo

        admin_profile.save()
        messages.success(request, f"Admin '{admin_profile.name}' updated successfully.")
        return redirect("admins:manage_admins")

    return render(request, "admins/edit_admin.html", {"admin_profile": admin_profile})


# ---------------- Toggle Admin Status ----------------
@login_required
@user_passes_test(is_super_admin)
def toggle_admin_status(request, admin_id):
    admin_profile = get_object_or_404(AdminProfile, id=admin_id)
    user = admin_profile.user
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"Admin '{admin_profile.name}' has been {status}.")
    return redirect("admins:manage_admins")


@admin_required
def admin_payment_slips(request):
    query = request.GET.get("q", "")
    month_filter = request.GET.get("month", "")  

    slips = PaymentSlip.objects.all().order_by("-uploaded_at")

    # Search by student name or room number
    if query:
        slips = slips.filter(
            Q(student__name__icontains=query) | Q(student__room_number__icontains=query)
        )

    # Filter by month (YYYY-MM)
    if month_filter:
        slips = slips.filter(month=month_filter)

    # Pagination (10 per page)
    paginator = Paginator(slips, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admins/admin_payment_slips.html",
        {
            "slips": page_obj,
            "query": query,
            "month_filter": month_filter,
            "page_title": "All Payment Slips",
        },
    )


@admin_required
def verify_payment_slip(request, slip_id):
    slip = get_object_or_404(PaymentSlip, id=slip_id)
    if not slip.is_verified:
        slip.is_verified = True
        slip.verified_by = request.user
        slip.save()
        messages.success(
            request, f"Payment for {slip.student.name} ({slip.month}) verified!"
        )
    else:
        messages.info(
            request,
            f"Payment for {slip.student.name} ({slip.month}) is already verified.",
        )
    return redirect("admins:admin_payment_slips")
