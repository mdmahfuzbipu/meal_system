from django.urls import path
from . import views

app_name = "votes"

urlpatterns = [
    path("", views.poll_list, name="poll_list"),
    path("create/", views.create_poll, name="create_poll"),
    path("<int:poll_id>/add-options/", views.add_options, name="add_options"),
    path("<int:poll_id>/vote/", views.cast_vote, name="cast_vote"),
    path("<int:poll_id>/results/", views.poll_results, name="poll_results"),
    path("<int:poll_id>/delete/", views.delete_poll, name="delete_poll"),
]
