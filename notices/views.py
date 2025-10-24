from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Notice, NoticeViewTracker
from .forms import NoticeForm


@login_required
def notice_list(request):
    notices = Notice.objects.all()
    
    tracker, created = NoticeViewTracker.objects.get_or_create(user=request.user)
    tracker.last_viewed = timezone.now()
    tracker.save()
    return render(request, "notices/notice_list.html", {"notices": notices})


@login_required
def create_notice(request):
    if request.user.role not in ["admin", "manager"]:
        messages.error(request, "You are not authorized to post notices.")
        return redirect("notices:notice_list")

    if request.method == "POST":
        form = NoticeForm(request.POST, request.FILES) 
        if form.is_valid():
            notice = form.save(commit=False)
            notice.posted_by = request.user
            notice.save()
            messages.success(request, "Notice posted successfully.")
            return redirect("notices:notice_list")
    else:
        form = NoticeForm()

    return render(request, "notices/create_notice.html", {"form": form})


@login_required
def edit_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)

    if request.user != notice.posted_by and request.user.role != "admin":
        messages.error(request, "You don't have permission to edit this notice.")
        return redirect("notices:notice_list")

    if request.method == "POST":
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, "Notice updated successfully!")
            return redirect("notices:notice_list")
    else:
        form = NoticeForm(instance=notice)

    return render(request, "notices/edit_notice.html", {"form": form, "notice": notice})


@login_required
def delete_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)

    if request.user != notice.posted_by and request.user.role != "admin":
        messages.error(request, "You don't have permission to delete this notice.")
        return redirect("notices:notice_list")

    if request.method == "POST":
        notice.delete()
        messages.success(request, "Notice deleted successfully!")
        return redirect("notices:notice_list")

    return render(request, "notices/confirm_delete.html", {"notice": notice})
