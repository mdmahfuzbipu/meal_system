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
    StudentMealPreference
)

from .forms import StudentMealPreferenceForm

from calendar import monthrange

# Create your views here.

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
        defaults={'status': True}  # Default is ON
    )

    try:
        tomorrow_status = DailyMealStatus.objects.get(student=student, date=tomorrow)
    except DailyMealStatus.DoesNotExist:
        tomorrow_status = None  # We'll use fallback in template

    if request.method == 'POST':
        status_value = request.POST.get("status")
        new_status = True if status_value == "on" else False
        DailyMealStatus.objects.update_or_create(
            student=student,
            date=tomorrow,
            defaults={'status': new_status}
        )
        return redirect('my_meal_status')

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
        "today_status": today_status.status,
        "tomorrow_status": (
            tomorrow_status.status if tomorrow_status else today_status.status
        ),
        "tomorrow_status_exists": bool(tomorrow_status),
        "today_date":today,
        "statuses": statuses,
    }

    return render(request, "students/my_meal_status.html", context)


@login_required
def update_tomorrow_meal_status(request):
    student = Student.objects.get(user=request.user)
    current_dt = localtime(now())

    cutoff_dt = current_dt.replace(
        hour=18, minute=0, second=0, microsecond=0
    )  # 18:00 or 6:00 PM

    if current_dt >= cutoff_dt:
        messages.error(
            request,
            "You can no longer change meal status for tomorrow. Deadline is 6:00 PM.",
        )
        return redirect("my_meal_status")

    tomorrow = current_dt.date() + timedelta(days=1)

    meal_status, _ = DailyMealStatus.objects.get_or_create(
        student=student,
        date=tomorrow,
        defaults={"status": False},  # Default to OFF if newly created
    )

    meal_status.status = not meal_status.status
    meal_status.save()

    status_text = "ON" if meal_status.status else "OFF"
    messages.success(request, f"Meal status for {tomorrow} is now {status_text}.")
    return redirect("my_meal_status")


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
                return redirect("update_meal_preference")

            meal_pref = form.save(commit=False)
            meal_pref.student = student
            meal_pref.month = month_str
            meal_pref.save()

            messages.success(request, f"Your Meal preferences for {month_display} updated.")
            return redirect("my_meal_preference")
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

    context = {
        "page_title": "Monthly Meal History",
        "statuses": statuses,
        "current_month": current_month,
    }
    return render(request, "students/meal_history.html", context)
