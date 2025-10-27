from django.contrib import admin
from .models import AdminProfile


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "user_type", "hall_role", "department", "assigned_floor")
    list_filter = ("user_type", "hall_role", "designation")
    search_fields = ("name", "employee_id", "department")
