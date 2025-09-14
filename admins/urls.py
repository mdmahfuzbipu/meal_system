from django.urls import path
from . import views

app_name = "admins"

urlpatterns = [
    path("register-student/", views.register_student, name="register_student"),
    path("manage-students/", views.manage_students, name="manage_students"),
    path("manage-staff/", views.manage_staff, name="manage_staff"),
    path("approvals/", views.approvals, name="approvals"),
    path("weekly-menu/", views.weekly_menu, name="weekly_menu"),
    path("meal-costs/", views.meal_costs, name="meal_costs"),
    path("analytics/", views.analytics, name="analytics"),
    # menu options
    path("menus/pending/", views.admin_menu_list, name="admin_menu_list"),
    path("menus/<int:proposal_id>/approve/", views.approve_menu, name="approve_menu"),
    path("menus/<int:proposal_id>/reject/", views.reject_menu, name="reject_menu"),
]
