from django.contrib import admin

from .models import ManagerProfile, WeeklyMenuProposal 

admin.site.register(WeeklyMenuProposal)

@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone_number", "nid", "created_at")
    search_fields = ("full_name", "user__username", "nid", "phone_number")
    readonly_fields = ("created_at", "updated_at")
