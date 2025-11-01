from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from django.utils.timezone import now, localtime, make_aware
from django.utils.dateformat import DateFormat

from datetime import date, timedelta, time, datetime
from calendar import monthrange

from accounts.decorators import student_required

from .models import (
    DailyMealCost,
    DailyMealStatus,
    MonthlyMealSummary,
    PaymentSlip, 
    Student,
    StudentMealPreference,
    WeeklyMenu, 
    Complaint,
    WeeklyMenuReview
)

from .forms import PaymentSlipForm, StudentMealPreferenceForm, WeeklyMenuReviewForm
from .utils import calculate_monthly_cost

from calendar import monthrange

# Create your views here.

@login_required
def monthly_summary(request):
    student = request.user.student
    today = date.today()

    monthly_cost = calculate_monthly_cost(student, today.year, today.month)

    context = {
        "student": student,
        "today": today,
        "monthly_cost": monthly_cost,
    }
    return render(request, "students/monthly_summary.html", context)


@login_required
def my_daily_meal_status(request):
    current_dt = localtime(now())
    today = current_dt.date()
    tomorrow = today + timedelta(days=1)
    current_year = today.year
    current_month = today.month

    student = Student.objects.get(user=request.user)

    # Get or create today's status
    today_status, _ = DailyMealStatus.objects.get_or_create(
        student=student,
        date=today,
        defaults={
            "breakfast_on": False,
            "lunch_on": False,
            "dinner_on": False,
        },
    )

    # Tomorrow defaults are copied from today's current values
    tomorrow_defaults = {
        "breakfast_on": today_status.breakfast_on,
        "lunch_on": today_status.lunch_on,
        "dinner_on": today_status.dinner_on,
    }

    tomorrow_status, created = DailyMealStatus.objects.get_or_create(
        student=student,
        date=tomorrow,
        defaults=tomorrow_defaults,
    )

    if request.method == "POST":
        tomorrow_status.breakfast_on = bool(request.POST.get("breakfast_on"))
        tomorrow_status.lunch_on = bool(request.POST.get("lunch_on"))
        tomorrow_status.dinner_on = bool(request.POST.get("dinner_on"))
        tomorrow_status.save()
        return redirect("students:my_meal_status")

    # Get current month's meal statuses
    first_day = date(current_year, current_month, 1)
    last_day = date(
        current_year, current_month, monthrange(current_year, current_month)[1]
    )
    statuses = DailyMealStatus.objects.filter(
        student=student, date__range=(first_day, last_day)
    ).order_by("-date")

    context = {
        "page_title": "Daily Meal Status",
        "today": today,
        "tomorrow": tomorrow,
        "today_status": today_status,
        "tomorrow_status": tomorrow_status,
        "tomorrow_status_exists": bool(tomorrow_status),
        "today_date": today,
        "statuses": statuses,
    }

    return render(request, "students/my_meal_status.html", context)


@login_required
def update_tomorrow_meal_status(request, meal_type):
    student = Student.objects.get(user=request.user)
    current_dt = localtime(now())

    cutoff_dt = current_dt.replace(hour=20, minute=0, second=0, microsecond=0)
    if current_dt >= cutoff_dt:
        messages.error(
            request,
            "You can no longer change meal status for tomorrow. Deadline is 8:00 PM.",
        )
        return redirect("students:my_meal_status")

    today = current_dt.date()
    tomorrow = today + timedelta(days=1)

    # Get today's status to inherit defaults
    today_status, _ = DailyMealStatus.objects.get_or_create(
        student=student,
        date=today,
        defaults={
            "breakfast_on": False,
            "lunch_on": False,
            "dinner_on": False,
        },
    )

    # Tomorrow inherits today's current values
    tomorrow_defaults = {
        "breakfast_on": today_status.breakfast_on,
        "lunch_on": today_status.lunch_on,
        "dinner_on": today_status.dinner_on,
    }

    meal_status, _ = DailyMealStatus.objects.get_or_create(
        student=student,
        date=tomorrow,
        defaults=tomorrow_defaults,
    )

    # Toggle the selected meal
    if meal_type == "breakfast":
        meal_status.breakfast_on = not meal_status.breakfast_on
    elif meal_type == "lunch":
        meal_status.lunch_on = not meal_status.lunch_on
    elif meal_type == "dinner":
        meal_status.dinner_on = not meal_status.dinner_on

    meal_status.save()

    messages.success(
        request, f"{meal_type.capitalize()} status updated for {tomorrow}."
    )
    return redirect("students:my_meal_status")


# get monthly meal preference
def get_month_str(dt):
    return dt.strftime("%Y-%m")


def get_or_create_meal_pref(student, month_str):
    pref=StudentMealPreference.objects.filter(student=student, month=month_str).first()

    if pref:
        return pref
    
    # if not pref found then use prev month
    year, month = map(int, month_str.split("-"))
    prev_month = date(year, month, 1) - timedelta(days=1)
    prev_month_str = get_month_str(prev_month)
    
    
    prev_pref = StudentMealPreference.objects.filter(student=student, month=prev_month_str).first()
    
    if prev_pref:
        return StudentMealPreference.objects.create(
            student=student,
            month = month_str,
            prefers_beef = prev_pref.prefers_beef,
            prefers_fish = prev_pref.prefers_fish,
        )

    # Fallback to student's default meal preference
    return StudentMealPreference.objects.create(
        student=student,
        month=month_str,
        prefers_beef = student.default_prefers_beef,
        prefers_fish = student.default_prefers_fish,
    )


@login_required
def my_meal_preference(request):
    student = Student.objects.get(user=request.user)
    current_dt = localtime(now())
    today = current_dt.date()

    current_month_str = get_month_str(today)
    next_month_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    next_month_str = get_month_str(next_month_date)

    current_month_display = DateFormat(today).format("F Y")
    next_month_display = DateFormat(next_month_date).format("F Y")

    cutoff_passed = today>=next_month_date

    current_pref = get_or_create_meal_pref(student, current_month_str)
    next_pref = get_or_create_meal_pref(student, next_month_str)

    context = {
        "page_title": "My Meal Preference",
        "current_month": current_month_display,
        "next_month": next_month_display,
        "current_pref": current_pref,
        "next_pref": next_pref,
        "cutoff_passed": cutoff_passed,
    }

    return render(request, "students/my_meal_preference.html", context)


from django.utils import timezone
from datetime import datetime, date, timedelta
from calendar import monthrange


@login_required
def update_multiple_days_meal_status(request):
    student = request.user.student
    current_dt = timezone.localtime(timezone.now())
    today = current_dt.date()
    tomorrow = today + timedelta(days=1)

    # Tomorrow cutoff time (8:00 PM today)
    tomorrow_cutoff = current_dt.replace(hour=20, minute=0, second=0, microsecond=0)

    # Month range
    current_year = today.year
    current_month = today.month
    first_day = date(current_year, current_month, 1)
    last_day = date(
        current_year, current_month, monthrange(current_year, current_month)[1]
    )
    month_dates = [
        first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)
    ]

    # Fetch existing statuses for the month
    statuses_qs = DailyMealStatus.objects.filter(
        student=student, date__range=(first_day, last_day)
    )
    statuses_dict = {s.date: s for s in statuses_qs}

    if request.method == "POST":
        # Loop over all future days
        for day in month_dates:
            if day < tomorrow:
                continue
            if day == tomorrow and current_dt >= tomorrow_cutoff:
                continue

            # Get or create DailyMealStatus
            status, _ = DailyMealStatus.objects.get_or_create(
                student=student,
                date=day,
                defaults={"breakfast_on": False, "lunch_on": False, "dinner_on": False},
            )

            # Update all meal statuses based on submitted checkboxes
            for meal_type in ["breakfast", "lunch", "dinner"]:
                checkbox_name = f"{meal_type}_{day.strftime('%Y-%m-%d')}"
                setattr(status, f"{meal_type}_on", checkbox_name in request.POST)

            status.save()

        messages.success(request, "Meal status updated successfully for future days!")
        return redirect("students:update_multiple_days_meal_status")

    # Prepare data for template
    month_statuses = []
    for day in month_dates:
        status = statuses_dict.get(day)
        # Determine disabled state
        if day < tomorrow:
            disabled = True
        elif day == tomorrow and current_dt >= tomorrow_cutoff:
            disabled = True
        else:
            disabled = False

        month_statuses.append(
            {
                "date": day,
                "breakfast_on": status.breakfast_on if status else True,
                "lunch_on": status.lunch_on if status else True,
                "dinner_on": status.dinner_on if status else True,
                "disabled": disabled,
            }
        )

    context = {
        "page_title": "Update Multiple Days Meal Status",
        "month_statuses": month_statuses,
        "today": today,
        "tomorrow": tomorrow,
        "tomorrow_cutoff_passed": current_dt >= tomorrow_cutoff,
    }
    return render(request, "students/update_multiple_days_meal_status.html", context)


@login_required
def update_meal_preference(request):
    student = Student.objects.get(user=request.user)
    current_date = now().date()
    current_dt = localtime(now())
    cutoff_dt = current_dt.replace(hour=18, minute=0, second=0, microsecond=0)

    next_month_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    month_str = get_month_str(next_month_date) # "2025-06"
    month_display = DateFormat(next_month_date).format('F Y') # July 2025

    # Get last day of current month
    last_day = monthrange(current_date.year, current_date.month)[1]
    cutoff_dt = current_date.replace(day=last_day)
    cutoff_dt = datetime.combine(cutoff_dt, time(18, 0))  # 6:00 PM
    cutoff_dt = timezone.make_aware(cutoff_dt)

    try:
        existing = StudentMealPreference.objects.get(student=student, month=month_str)
    except StudentMealPreference.DoesNotExist:
        existing = None

    if request.method == "POST":
        form = StudentMealPreferenceForm(request.POST, instance=existing)
        if form.is_valid():
            if current_dt >= cutoff_dt:
                messages.error(
                    request, "You cannot change meal preference after the month starts and after 6:00 PM of the last day."
                )
                return redirect("students:update_meal_preference")

            meal_pref = form.save(commit=False)
            meal_pref.student = student
            meal_pref.month = month_str
            meal_pref.save()

            messages.success(request, f"Your Meal preferences for {month_display} updated.")
            return redirect("students:my_meal_preference")
    else:
        form = StudentMealPreferenceForm(instance=existing)

    context = {
        "page_title":"Update Meal Preference",
        "form": form,
        "month": month_display,
        "existing": existing,
    }

    return render(request, "students/update_meal_preference.html", context)


def _parse_selected_month(param):
    if param:
        y, m = map(int, param.split("-"))
    else:
        now_dt = now()
        y, m = now_dt.year, now_dt.month
    return y, m


def _get_month_display(year, month):
    return datetime(year, month, 1).strftime("%B %Y")


def _get_preferences(student_obj, year, month):
    pref = StudentMealPreference.objects.filter(
        student=student_obj, month=f"{year}-{month:02d}"
    ).first()
    return (
        pref.prefers_beef if pref else student_obj.default_prefers_beef,
        pref.prefers_fish if pref else student_obj.default_prefers_fish,
    )


def _get_menu_for_weekday(weekday):
    return WeeklyMenu.objects.filter(day_of_week=weekday).first()


def _compute_daily_cost(menu, status_obj, prefers_beef, prefers_fish):
    if not menu:
        return 0

    def _meal_cost(on, contains_beef, contains_fish, base_cost, alt_cost):
        if not on:
            return 0
        if contains_beef and not prefers_beef:
            return alt_cost
        if contains_fish and not prefers_fish:
            return alt_cost
        return base_cost

    cost = 0
    # Breakfast has no alternate cost logic, just add if on
    cost += _meal_cost(
        status_obj.breakfast_on,
        False,
        False,
        getattr(menu, "breakfast_cost", 0),
        0,
    )

    cost += _meal_cost(
        status_obj.lunch_on,
        getattr(menu, "lunch_contains_beef", False),
        getattr(menu, "lunch_contains_fish", False),
        getattr(menu, "lunch_cost", 0),
        getattr(menu, "lunch_cost_alternate", 0),
    )

    cost += _meal_cost(
        status_obj.dinner_on,
        getattr(menu, "dinner_contains_beef", False),
        getattr(menu, "dinner_contains_fish", False),
        getattr(menu, "dinner_cost", 0),
        getattr(menu, "dinner_cost_alternate", 0),
    )

    return cost


@login_required
def meal_history(request):
    student = request.user.student

    selected_month = request.GET.get("month")
    year, month = _parse_selected_month(selected_month)
    month_name = _get_month_display(year, month)

    prefers_beef, prefers_fish = _get_preferences(student, year, month)

    statuses_qs = DailyMealStatus.objects.filter(
        student=student, date__year=year, date__month=month
    ).order_by("date")

    updated_statuses = []
    total_month_cost = 0

    for status in statuses_qs:
        weekday = status.date.strftime("%A")
        menu = _get_menu_for_weekday(weekday)
        daily_cost = _compute_daily_cost(menu, status, prefers_beef, prefers_fish)
        total_month_cost += daily_cost

        total_on = (
            (1 if status.breakfast_on else 0)
            + (1 if status.lunch_on else 0)
            + (1 if status.dinner_on else 0)
        )

        updated_statuses.append(
            {
                "date": status.date,
                "weekday": weekday,
                "breakfast_on": status.breakfast_on,
                "lunch_on": status.lunch_on,
                "dinner_on": status.dinner_on,
                "total_on": total_on,
                "daily_cost": daily_cost,
            }
        )

    context = {
        "page_title": "Monthly Meal History",
        "statuses": updated_statuses,
        "prefers_beef": prefers_beef,
        "prefers_fish": prefers_fish,
        "current_month": month_name,
        "selected_month": f"{year}-{month:02d}",
        "total_month_cost": total_month_cost,
    }

    return render(request, "students/meal_history.html", context)


@login_required
def weekly_menu_view(request):
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    weekly_menu = list(WeeklyMenu.objects.all())
    weekly_menu.sort(key=lambda x: days_order.index(x.day_of_week))

    return render(
        request,
        "students/weekly_menu.html",
        {"page_title": "Weekly Menu", "weekly_menu": weekly_menu},
    )


@login_required
def submit_complaint(request):
    student = request.user.student
    if request.method == "POST":
        name = request.POST.get("name")
        room = request.POST.get("room_number")
        phone = request.POST.get("phone_number")
        desc = request.POST.get("description")

        if not all([name, room, phone, desc]):
            messages.error(request, "All fields are required.")
            return redirect("students:submit_complaint")

        Complaint.objects.create(
            student=student,
            name=name,
            room_number=room,
            phone_number=phone,
            description=desc,
        )
        messages.success(request, "Complaint submitted successfully!")
        return redirect("students:submit_complaint")

    return render(
        request,
        "students/submit_complaint.html",
        {"page_title": "Complaint Box",},
    )


@student_required
def submit_review(request):
    if request.method == "POST":
        form = WeeklyMenuReviewForm(request.POST)
        if form.is_valid():
            review, created = WeeklyMenuReview.objects.update_or_create(
                student=request.user.student,
                day_of_week=form.cleaned_data["day_of_week"],
                meal_type=form.cleaned_data["meal_type"],
                defaults={
                    "rating": form.cleaned_data["rating"],
                    "comment": form.cleaned_data["comment"],
                },
            )
            if created:
                messages.success(request, "Review submitted successfully!")
            else:
                messages.info(request, "Your review has been updated.")
            return redirect("students:reviews_list")
    else:
        form = WeeklyMenuReviewForm()
    return render(
        request,
        "students/submit_review.html",
        {"form": form, "page_title": "Submit Review"},
    )


@login_required
def reviews_list(request):
    """Show aggregated ratings and recent reviews"""
    agg = (
        WeeklyMenuReview.objects.values("day_of_week", "meal_type")
        .annotate(avg_rating=Avg("rating"), total_reviews=Count("id"))
        .order_by("day_of_week", "meal_type")
    )
    recent_reviews = WeeklyMenuReview.objects.select_related("student").order_by(
        "-created_at"
    )[:10]
    return render(
        request,
        "students/reviews_list.html",
        {
            "aggregated": agg,
            "recent_reviews": recent_reviews,
            "page_title": "Weekly Food Reviews",
        },
    )


@login_required
def profile_view(request):
    """Display the logged-in student's full profile info"""
    student = request.user.student

    from .models import StudentDetails, StudentMealPreference
    import datetime

    try:
        details = StudentDetails.objects.get(student=student)
    except StudentDetails.DoesNotExist:
        details = None

    latest_meal = (
        StudentMealPreference.objects.filter(student=student)
        .order_by("-month", "-created_at")  # latest month first
        .first()
    )

    context = {
        "page_title": "My Profile",
        "student": student,
        "details": details,
        "latest_meal": latest_meal, 
    }
    return render(request, "students/profile.html", context)


@student_required
def upload_payment_slip(request):
    student = request.user.student  # Only their own Student object
    if request.method == "POST":
        form = PaymentSlipForm(request.POST, request.FILES)
        if form.is_valid():
            slip = form.save(commit=False)
            slip.student = student
            slip.save()
            messages.success(request, "Payment slip uploaded successfully!")
            return redirect("students:upload_payment_slip")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Show existing slips of the student only
        slips = PaymentSlip.objects.filter(student=student).order_by("-uploaded_at")
        form = PaymentSlipForm()
    return render(
        request,
        "students/upload_payment_slip.html",
        {"form": form, "page_title": "Upload Payment Slip", "slips": slips},
    )
