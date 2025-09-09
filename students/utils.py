from .models import DailyMealStatus, WeeklyMenu, StudentMealPreference
from datetime import date, timedelta
from calendar import monthrange
from decimal import Decimal

def _get_meal_cost(contains_beef, contains_fish, prefers_beef, prefers_fish, cost, cost_alternate):
    if contains_beef and not prefers_beef:
        return cost_alternate
    if contains_fish and not prefers_fish:
        return cost_alternate
    return cost

def calculate_daily_cost(student, current_date):
    try:
        status = DailyMealStatus.objects.get(student=student, date=current_date)
        menu = WeeklyMenu.objects.get(
            day_of_week=current_date.strftime("%A")
        ) 

        # Get student's preference for that month
        month_str = current_date.strftime("%Y-%m")
        preference = StudentMealPreference.objects.filter(student=student, month=month_str).first()
        prefers_beef = preference.prefers_beef if preference else student.default_prefers_beef
        prefers_fish = preference.prefers_fish if preference else student.default_prefers_fish

    except (DailyMealStatus.DoesNotExist, WeeklyMenu.DoesNotExist):
        return Decimal("0.00")

    cost = Decimal("0.00")

    # Breakfast
    if status.breakfast_on:
        cost += menu.breakfast_cost  

    # Lunch
    if status.lunch_on:
        cost += _get_meal_cost(
            menu.lunch_contains_beef,
            menu.lunch_contains_fish,
            prefers_beef,
            prefers_fish,
            menu.lunch_cost,
            menu.lunch_cost_alternate
        )

    # Dinner
    if status.dinner_on:
        cost += _get_meal_cost(
            menu.dinner_contains_beef,
            menu.dinner_contains_fish,
            prefers_beef,
            prefers_fish,
            menu.dinner_cost,
            menu.dinner_cost_alternate
        )

    return cost


def calculate_monthly_cost(student, year, month):
    days_in_month = monthrange(year, month)[1]  # Total days in month
    total_cost = Decimal("0.00")

    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        total_cost += calculate_daily_cost(student, current_date)

    return total_cost
