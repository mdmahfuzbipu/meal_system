from django.urls import path
from . import views

app_name = "students"

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
    path(
        "meal-status/update/",
        views.update_multiple_days_meal_status,
        name="update_multiple_days_meal_status",
    ),
    path("meal-history/", views.meal_history, name="meal_history"),
    path("weekly-menu/", views.weekly_menu_view, name="weekly_menu"),
    path("submit-complaint/", views.submit_complaint, name="submit_complaint"),
    path("reviews/submit/", views.submit_review, name="submit_review"),
    path("reviews/", views.reviews_list, name="reviews_list"),
    path("profile/", views.profile_view, name="profile"),
    path("payment/upload/", views.upload_payment_slip, name="upload_payment_slip"),
]
