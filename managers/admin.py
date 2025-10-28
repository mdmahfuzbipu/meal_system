from django.contrib import admin

from .models import ManagerProfile, MealToken, WeeklyMenuProposal, SpecialMealRequest

admin.site.register(WeeklyMenuProposal)

@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone_number", "nid", "created_at")
    search_fields = ("full_name", "user__username", "nid", "phone_number")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SpecialMealRequest)
class SpecialMealRequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "requested_date",
        "meal_type",
        "manager",
        "created_by",
        "status",
        "created_at",
    )
    list_filter = ("status", "meal_type", "requested_date")
    search_fields = (
        "title",
        "description",
        "created_by__username",
        "manager__username",
    )


@admin.register(MealToken)
class MealTokenAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "date",
        "meal_type",
        "token_type",
        "collected",
        "issued_by",
        "issued_at",
    )
    list_filter = ("date", "meal_type", "token_type", "collected")
    search_fields = ("student__name", "student__room_number")
    ordering = ("-issued_at",)
    date_hierarchy = "date"
    list_per_page = 25
