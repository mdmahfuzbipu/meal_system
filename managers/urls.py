from django.urls import path
from . import views

urlpatterns = [
    # Manager
    path("menus/", views.manager_menu_list, name="manager_menu_list"),
    path("menus/create/", views.create_weekly_menu, name="create_weekly_menu"),
]