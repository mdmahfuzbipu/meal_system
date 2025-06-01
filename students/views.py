from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now, localtime


from datetime import date, timedelta, time


from .models import (
    DailyMealStatus, 
    Student,
    StudentMealPreference
)

from .forms import StudentMealPrefereceForm

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
def update_meal_preference(request):
    student = Student.objects.get(user=request.user)
    current_date = now().date()
    next_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    month_str = next_month.strftime("%Y-%m") # "2025-06"
    
    try:
        existing = StudentMealPreference.objects.get(student=student, month=month_str)
    except StudentMealPreference.DoesNotExist:
        existing = None
        
    
    if request.method == "POST":
        form = StudentMealPrefereceForm(request.POST)
        if form.is_valid():
            if current_date >= next_month:
                messages.error(request, "You can not change meal type after the month starts.")
                return redirect("update_meal_preference")
            
            prefers_beef = form.cleaned_data["prefers_beef"]
            prefers_fish = form.cleaned_data["prefers_fish"]  
            
            StudentMealPreference.objects.update_or_create(
                student=student,
                month=month_str,
                defaults={"prefers_beef": prefers_beef, "prefers_fish":prefers_fish}
            )
            messages.success(request, f"Meal preferences for {month_str} updated.")
            return redirect("update_meal_preference")
    else:
        form = StudentMealPrefereceForm(initial={
            "prefers_beef": existing.prefers_beef if existing else True,
            "prefers_fish": existing.prefers_fish if existing else True
        })
        
    context = {
        "page_title":"Update Meal Preference",
        "form": form,
        "month": month_str,
        "existing": existing,
    }
    
    return render(request, "students/update_meal_preference.html", context)
