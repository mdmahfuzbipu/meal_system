from django.urls import path
from . import views

app_name = "admins"

urlpatterns = [
    path("manage-students/", views.manage_students, name="manage_students"),
    path("manage-staff/", views.manage_staff, name="manage_staff"),
    path("approvals/", views.approvals, name="approvals"),
    path("weekly-menu/", views.weekly_menu, name="weekly_menu"),
    path("meal-costs/", views.meal_costs, name="meal_costs"),
    path("analytics/", views.analytics, name="analytics"),
]
