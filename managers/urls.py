from django.urls import path
from . import views

app_name = "managers"

urlpatterns = [
    path("menus/", views.manager_menu_list, name="manager_menu_list"),
    path("propose-weekly-menu/", views.propose_weekly_menu, name="propose_weekly_menu"),
    path("monthly-summary/", views.monthly_summary_view, name="monthly_summary"),
    path(
        "export-monthly-summary/",
        views.export_monthly_summary,
        name="export_monthly_summary",
    ),
    path("manage-complaints/", views.manage_complaints, name="manage_complaints"),
    path(
        "special-requests/create/",
        views.create_special_request,
        name="create_special_request",
    ),
    path(
        "special_requests/", views.manager_requests_list, name="manager_requests_list"
    ),
    path(
        "special-requests/<int:pk>/",
        views.manager_request_detail,
        name="manager_request_detail",
    ),
]
