from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import WeeklyMenuProposal
from students.models import WeeklyMenu, WEEKDAY_CHOICES
from .forms import WeeklyMenuProposalForm
from accounts.decorators import manager_required
from datetime import date, timedelta


def is_manager(user):
    return user.role == "manager"


def is_admin(user):
    return user.role == "admin"


@login_required
@user_passes_test(is_manager)
def manager_menu_list(request):
    proposals = WeeklyMenuProposal.objects.filter(created_by=request.user)
    return render(request, "managers/manager_menu_list.html", {"proposals": proposals})


@manager_required
def propose_weekly_menu(request):
    current_week_start = WeeklyMenuProposal.get_week_start()

    if request.method == "POST":
        # Remove old pending proposals for this week
        WeeklyMenuProposal.objects.filter(
            week_start_date=current_week_start,
            created_by=request.user,
            status="pending",
        ).delete()

        forms_valid = True

        # Loop through 7 days
        for day, _ in WEEKDAY_CHOICES:
            form = WeeklyMenuProposalForm(
                {
                    "day_of_week": day,
                    "week_start_date": current_week_start,
                    "breakfast_main": request.POST.get(f"{day}_breakfast_main", ""),
                    "breakfast_cost": request.POST.get(f"{day}_breakfast_cost", 0),
                    "lunch_main": request.POST.get(f"{day}_lunch_main", ""),
                    "lunch_cost": request.POST.get(f"{day}_lunch_cost", 0),
                    "lunch_contains_beef": request.POST.get(
                        f"{day}_lunch_contains_beef"
                    )
                    == "on",
                    "lunch_contains_fish": request.POST.get(
                        f"{day}_lunch_contains_fish"
                    )
                    == "on",
                    "lunch_alternate": request.POST.get(f"{day}_lunch_alternate", ""),
                    "lunch_cost_alternate": request.POST.get(
                        f"{day}_lunch_cost_alternate", 0
                    ),
                    "dinner_main": request.POST.get(f"{day}_dinner_main", ""),
                    "dinner_cost": request.POST.get(f"{day}_dinner_cost", 0),
                    "dinner_contains_beef": request.POST.get(
                        f"{day}_dinner_contains_beef"
                    )
                    == "on",
                    "dinner_contains_fish": request.POST.get(
                        f"{day}_dinner_contains_fish"
                    )
                    == "on",
                    "dinner_alternate": request.POST.get(f"{day}_dinner_alternate", ""),
                    "dinner_cost_alternate": request.POST.get(
                        f"{day}_dinner_cost_alternate", 0
                    ),
                }
            )

            if form.is_valid():
                proposal = form.save(commit=False)
                proposal.created_by = request.user
                proposal.week_start_date = current_week_start
                proposal.save()
            else:
                forms_valid = False
                print(form.errors)

        # Final message
        if forms_valid:
            messages.success(
                request,
                f"✅ Weekly proposal for week starting {current_week_start} submitted!",
            )
            return redirect("managers:propose_weekly_menu")
        else:
            messages.error(request, "❌ Some fields were invalid. Please check again.")

    
    return render(
        request,
        "managers/propose_weekly_menu.html",
        {"weekdays": WEEKDAY_CHOICES, "week_start_date": current_week_start},
    )
