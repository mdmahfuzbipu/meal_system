from django.urls import path
from . import views

app_name = "managers"

urlpatterns = [

    path("menus/", views.manager_menu_list, name="manager_menu_list"),
    path("propose-weekly-menu/", views.propose_weekly_menu, name="propose_weekly_menu"),
]
