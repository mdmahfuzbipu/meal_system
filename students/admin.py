from django.contrib import admin
from .models import (
    Student,
    StudentDetails,
    StudentMealPreference,
    WeeklyMenu,
    DailyMealStatus,
    DailyMealCost,
    MonthlyMealSummary,
    Complain,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "room_number", "created_at")
    search_fields = ("name", "room_number")
    ordering = ("room_number",)


@admin.register(StudentDetails)
class StudentDetailsAdmin(admin.ModelAdmin):
    list_display = ("student", "university_id", "department", "batch", "phone_number")
    search_fields = ("student__name", "university_id", "national_id")
    list_filter = ("department", "batch", "blood_group")


@admin.register(StudentMealPreference)
class StudentMealPreferenceAdmin(admin.ModelAdmin):
    list_display = ("student", "month", "prefers_beef", "prefers_fish")
    list_filter = ("month", "prefers_beef", "prefers_fish")
    search_fields = ("student__name",)


# @admin.register(WeeklyMenu)
# class WeeklyMenuAdmin(admin.ModelAdmin):
#     list_display = (
#         "day_of_week",
#         "includes_beef",
#         "includes_fish",
#         "base_cost",
#         "alternate_cost",
#     )
#     list_filter = ("includes_beef", "includes_fish")
#     ordering = ("day_of_week",)


@admin.register(WeeklyMenu)
class WeeklyMenuAdmin(admin.ModelAdmin):
    list_display = (
        "day_of_week",
        "breakfast_main",
        "breakfast_cost",
        "lunch_main",
        "lunch_cost",
        "dinner_main",
        "dinner_cost",
    )
    list_filter = ("day_of_week",)


@admin.register(DailyMealStatus)
class DailyMealStatusAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "breakfast_on", "lunch_on", "dinner_on")
    list_filter = ("date", "breakfast_on", "lunch_on", "dinner_on")
    search_fields = ("student__name",)


@admin.register(DailyMealCost)
class DailyMealCostAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "total_cost")
    list_filter = ("date",)
    search_fields = ("student__name",)


@admin.register(MonthlyMealSummary)
class MonthlyMealSummaryAdmin(admin.ModelAdmin):
    list_display = ("student", "month", "total_on_days", "total_cost")
    list_filter = ("month",)
    search_fields = ("student__name",)


@admin.register(Complain)
class ComplainAdmin(admin.ModelAdmin):
    list_display = ("name", "room_number", "phone", "is_resolved", "submitted_at")
    list_filter = ("is_resolved",)
    search_fields = ("name", "room_number", "phone", "description")
