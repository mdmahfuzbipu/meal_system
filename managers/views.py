from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import WeeklyMenuProposal
from students.models import WeeklyMenu


# Create your views here.


def is_manager(user):
    return user.role == "manager"


def is_admin(user):
    return user.role == "admin"


@login_required
@user_passes_test(is_manager)
def manager_menu_list(request):
    proposals = WeeklyMenuProposal.objects.filter(created_by=request.user)
    return render(request, "managers/manager_menu_list.html", {"proposals": proposals})


@login_required
@user_passes_test(is_manager)
def create_weekly_menu(request):
    if request.method == "POST":
        day_of_week = request.POST.get("day_of_week")
        breakfast_main = request.POST.get("breakfast_main")
        breakfast_cost = request.POST.get("breakfast_cost")
        lunch_main = request.POST.get("lunch_main")
        lunch_cost = request.POST.get("lunch_cost")
        lunch_contains_beef = bool(request.POST.get("lunch_contains_beef"))
        lunch_contains_fish = bool(request.POST.get("lunch_contains_fish"))
        dinner_main = request.POST.get("dinner_main")
        dinner_cost = request.POST.get("dinner_cost")
        dinner_contains_beef = bool(request.POST.get("dinner_contains_beef"))
        dinner_contains_fish = bool(request.POST.get("dinner_contains_fish"))

        WeeklyMenuProposal.objects.create(
            day_of_week=day_of_week,
            breakfast_main=breakfast_main,
            breakfast_cost=breakfast_cost,
            lunch_main=lunch_main,
            lunch_cost=lunch_cost,
            lunch_contains_beef=lunch_contains_beef,
            lunch_contains_fish=lunch_contains_fish,
            dinner_main=dinner_main,
            dinner_cost=dinner_cost,
            dinner_contains_beef=dinner_contains_beef,
            dinner_contains_fish=dinner_contains_fish,
            created_by=request.user,
        )

        messages.success(request, "Weekly menu proposal created successfully!")
        return redirect("manager_menu_list")

    return render(request, "managers/create_weekly_menu.html")
