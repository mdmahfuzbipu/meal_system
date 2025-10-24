from django.urls import path
from . import views

app_name = 'notices'

urlpatterns = [
    path("", views.notice_list, name="notice_list"),
    path("create/", views.create_notice, name="create_notice"),
    path("<int:pk>/edit/", views.edit_notice, name="edit_notice"),
    path("<int:pk>/delete/", views.delete_notice, name="delete_notice"),
]
