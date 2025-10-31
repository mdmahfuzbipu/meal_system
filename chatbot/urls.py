from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("ask/", views.chat_api, name="chat_api"),
    path("", views.chat_page, name="chat_page"),  
]