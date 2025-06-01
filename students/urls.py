from django.urls import path
from . import views

urlpatterns = [
    path("my-meal-status/", views.my_daily_meal_status, name="my_meal_status"),
    path(
        "update-tomorrow-status/",
        views.update_tomorrow_meal_status,
        name="update_tomorrow_status",
    ),
    path("update-meal-preference", views.update_meal_preference, name="update_meal_preference"),
]
