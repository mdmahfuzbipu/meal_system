from django.urls import path
from . import views

urlpatterns = [
    path("my-meal-status/", views.my_daily_meal_status, name="my_meal_status"),
    path(
        "update-tomorrow-status/<str:meal_type>/",
        views.update_tomorrow_meal_status,
        name="update_tomorrow_status",
    ),
    path(
        "update-meal-preference",
        views.update_meal_preference,
        name="update_meal_preference",
    ),
    path("my-meal-preference", views.my_meal_preference, name="my_meal_preference"),
    path("meal-history/", views.meal_history, name="meal_history"),
    path("weekly-menu/", views.weekly_menu_view, name="weekly_menu"),
    path("complain/", views.complain_create, name="complain_create"),
    path("monthly-summary/", views.monthly_summary, name="monthly_summary"),
]
