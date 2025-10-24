from django.urls import path
from . import views

app_name = "admins"

urlpatterns = [
    path("register-manager/", views.register_manager, name="register_manager"),
    path("manage-managers/", views.manage_managers, name="manage_managers"),
    path("edit/<int:manager_id>/", views.edit_manager, name="edit_manager"),
    path(
        "toggle-manager-status/<int:manager_id>/",
        views.toggle_manager_status,
        name="toggle_manager_status",
    ),
    path("register-student/", views.register_student, name="register_student"),
    path("manage-students/", views.manage_students, name="manage_students"),
    path("edit-student/<int:student_id>/", views.edit_student, name="edit_student"),
    path(
        "toggle-student-status/<int:student_id>/",
        views.toggle_student_status,
        name="toggle_student_status",
    ),
    path("manage-staff/", views.manage_staff, name="manage_staff"),
    path("approvals/", views.approvals, name="approvals"),
    path("weekly-menu/", views.weekly_menu, name="weekly_menu"),
    path("meal-costs/", views.meal_costs, name="meal_costs"),
    path("analytics/", views.analytics, name="analytics"),
    # menu options
    path(
        "review-weekly-proposals/",
        views.review_weekly_proposals,
        name="review_weekly_proposals",
    ),
    path("menus/pending/", views.admin_menu_list, name="admin_menu_list"),
    path("menus/<int:proposal_id>/approve/", views.approve_menu, name="approve_menu"),
    path("menus/<int:proposal_id>/reject/", views.reject_menu, name="reject_menu"),
    path("view-complaints/", views.view_complaints, name="view_complaints"),
]
