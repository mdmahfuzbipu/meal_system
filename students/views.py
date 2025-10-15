from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now, localtime, make_aware
from django.utils.dateformat import DateFormat

from datetime import date, timedelta, time, datetime
from calendar import monthrange

from .models import (
    DailyMealStatus, 
    Student,
    StudentMealPreference,
    WeeklyMenu
)

from .forms import StudentMealPreferenceForm, ComplainForm
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

    today_status, _ = DailyMealStatus.objects.get_or_create(
        student=student,
        date=today,
        defaults={
            "breakfast_on": True,
            "lunch_on": True,
            "dinner_on": True,
        },  
    )

    # Tomorrow's meal status
    tomorrow_status, _ = DailyMealStatus.objects.get_or_create(
        student=student,
        date=tomorrow,
        defaults={"breakfast_on": True, "lunch_on": True, "dinner_on": True},
    )

    if request.method == "POST":
        tomorrow_status.breakfast_on = bool(request.POST.get("breakfast_on"))
        tomorrow_status.lunch_on = bool(request.POST.get("lunch_on"))
        tomorrow_status.dinner_on = bool(request.POST.get("dinner_on"))
        tomorrow_status.save()
        return redirect("students:my_meal_status")

    first_day = date(current_year, current_month, 1)
    last_day = date(
        current_year, current_month, monthrange(current_year, current_month)[1]
    )

    statuses = DailyMealStatus.objects.filter(
        student=student,
        date__range=(first_day, last_day)
    ).order_by('-date')

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

    cutoff_dt = current_dt.replace(
        hour=20, minute=0, second=0, microsecond=0
    )  # 18:00 or 6:00 PM

    if current_dt >= cutoff_dt:
        messages.error(
            request,
            "You can no longer change meal status for tomorrow. Deadline is 8:00 PM.",
        )
        return redirect("students:my_meal_status")

    tomorrow = current_dt.date() + timedelta(days=1)

    meal_status, _ = DailyMealStatus.objects.get_or_create(
        student=student,
        date=tomorrow,
        defaults={
            "breakfast_on": True,
            "lunch_on": True,
            "dinner_on": True,
        },  
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


@login_required
def meal_history(request):
    student = request.user.student
    current_month = now().strftime("%B %Y")

    statuses = DailyMealStatus.objects.filter(
        student=student, date__year=now().year, date__month=now().month
    ).order_by("date")

    # Prepare list with total_on
    updated_statuses = []
    for status in statuses:
        total_on = sum(
            [
                1 if status.breakfast_on else 0,
                1 if status.lunch_on else 0,
                1 if status.dinner_on else 0,
            ]
        )
        updated_statuses.append(
            {
                "date": status.date,
                "breakfast_on": status.breakfast_on,
                "lunch_on": status.lunch_on,
                "dinner_on": status.dinner_on,
                "total_on": total_on,
            }
        )

    context = {
        "page_title": "Monthly Meal History",
        "statuses": updated_statuses,
        "current_month": current_month,
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
def complain_create(request):
    if request.method == "POST":
        form = ComplainForm(request.POST)
        if form.is_valid():
            complain = form.save(commit=False)
            complain.user = request.user
            complain.save()
            messages.success(request, "Your complaint has been submitted successfully.")
            return redirect("home")  
    else:
        form = ComplainForm()
    return render(
        request,
        "students/complain_form.html",
        {"page_title": "Complain Box", "form": form},
    )
