from django.urls import path
from . import api_views

urlpatterns = [
    path("menu/today/", api_views.today_menu, name="api_today_menu"),
    path(
        "meal-status/today/", api_views.today_meal_status, name="api_today_meal_status"
    ),
    path("meal-cost/today/", api_views.today_meal_cost, name="api_today_meal_cost"),
    path("monthly-summary/", api_views.monthly_summary, name="api_monthly_summary"),
    path(
        "meal/review/today/", api_views.today_meal_review, name="api_today_meal_review"
    ),
    path("complaints/my/", api_views.my_complaints, name="api_my_complaints"),
    path("student/profile/", api_views.student_profile, name="api_student_profile"),
    path("notices/today/", api_views.today_notices, name="api_today_notices"),
]
