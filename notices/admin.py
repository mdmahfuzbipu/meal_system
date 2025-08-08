from django.contrib import admin
from .models import Notice


# Register your models here.
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title", "content")
