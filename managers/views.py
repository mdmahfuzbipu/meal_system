from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from openpyxl import Workbook

from students.utils import generate_monthly_summary_for_all

from students.models import MonthlyMealSummary, StudentMealPreference
from .models import WeeklyMenuProposal
from students.models import MonthlyMealSummary, WeeklyMenu, WEEKDAY_CHOICES
from .forms import WeeklyMenuProposalForm
from accounts.decorators import manager_required
from datetime import date, datetime, timedelta


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


from django.shortcuts import render
from django.db.models import Sum
from students.models import MonthlyMealSummary, StudentMealPreference
from accounts.decorators import manager_required  # if using custom decorator


@manager_required
def monthly_summary_view(request):
    months = (
        MonthlyMealSummary.objects.values_list("month", flat=True)
        .distinct()
        .order_by("-month")
    )
    selected_month = request.GET.get("month")
    filter_type = request.GET.get("type")  # 'beef_fish' or 'mutton_egg'

    summaries = []
    total_cost = 0

    # preference stats
    beef_count = no_beef_count = fish_count = no_fish_count = 0

    if selected_month:
        # Load summaries for the selected month
        summaries = MonthlyMealSummary.objects.filter(
            month=selected_month
        ).select_related("student")

        # Attach meal preferences for each student
        prefs = {
            p.student_id: p
            for p in StudentMealPreference.objects.filter(month=selected_month)
        }

        for s in summaries:
            pref = prefs.get(s.student.id)
            s.prefers_beef = pref.prefers_beef if pref else True
            s.prefers_fish = pref.prefers_fish if pref else True

        # Compute statistics
        beef_count = sum(1 for s in summaries if s.prefers_beef)
        no_beef_count = sum(1 for s in summaries if not s.prefers_beef)
        fish_count = sum(1 for s in summaries if s.prefers_fish)
        no_fish_count = sum(1 for s in summaries if not s.prefers_fish)

        # Optional filtering for table view
        if filter_type == "beef_fish":
            summaries = [s for s in summaries if s.prefers_beef and s.prefers_fish]
        elif filter_type == "mutton_egg":
            summaries = [
                s for s in summaries if not s.prefers_beef or not s.prefers_fish
            ]

        # Calculate total cost
        total_cost = sum(float(s.total_cost) for s in summaries)

    return render(
        request,
        "managers/monthly_summary.html",
        {
            "months": months,
            "selected_month": selected_month,
            "summaries": summaries,
            "total_cost": total_cost,
            "filter_type": filter_type,
            "beef_count": beef_count,
            "no_beef_count": no_beef_count,
            "fish_count": fish_count,
            "no_fish_count": no_fish_count,
        },
    )


def _get_summaries_and_prefs(month):
    summaries = (
        MonthlyMealSummary.objects.filter(month=month)
        .select_related("student")
        .order_by("student__room_number")
    )
    prefs = {p.student_id: p for p in StudentMealPreference.objects.filter(month=month)}
    return summaries, prefs


def _determine_pref_values(s, prefs):
    pref = prefs.get(s.student.id)
    prefers_beef = pref.prefers_beef if pref else getattr(s.student, "default_prefers_beef", True)
    prefers_fish = pref.prefers_fish if pref else getattr(s.student, "default_prefers_fish", True)
    return prefers_beef, prefers_fish


def _meal_type_label(prefers_beef, prefers_fish):
    if prefers_beef and prefers_fish:
        return "Beef + Fish"
    if not prefers_beef and prefers_fish:
        return "Mutton + Fish"
    if prefers_beef and not prefers_fish:
        return "Beef + Egg"
    return "Mutton + Egg"


def _build_workbook(summaries, prefs, month):
    wb = Workbook()
    ws = wb.active
    ws.title = f"Summary_{month}"

    headers = [
        "Room Number",
        "Student Name",
        "Total ON Days",
        "Prefers Beef",
        "Prefers Fish",
        "Meal Type",
        "Total Cost (৳)",
    ]
    ws.append(headers)

    for s in summaries:
        prefers_beef, prefers_fish = _determine_pref_values(s, prefs)
        meal_type = _meal_type_label(prefers_beef, prefers_fish)

        ws.append(
            [
                s.student.room_number,
                s.student.name,
                s.total_on_days,
                "Yes" if prefers_beef else "No",
                "Yes" if prefers_fish else "No",
                meal_type,
                float(s.total_cost),
            ]
        )

    # Style header row
    for cell in ws[1]:
        cell.font = cell.font.copy(bold=True)

    # Adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[column].width = max_length + 2

    return wb


@manager_required
def export_monthly_summary(request):
    month = request.GET.get("month")
    if not month:
        return HttpResponse("Month parameter missing.", status=400)

    summaries, prefs = _get_summaries_and_prefs(month)
    wb = _build_workbook(summaries, prefs, month)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"Meal_Summary_{month}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response
