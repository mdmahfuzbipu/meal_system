from django.shortcuts import render
from .models import Notice


# Create your views here.
def notice_list(request):
    notices = Notice.objects.all()
    return render(request, "notices/notice_list.html", {"page_title": "Notice Board","notices": notices})
