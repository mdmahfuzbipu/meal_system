from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import admin_required, student_required, manager_required
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import VotePoll, VoteOption, Vote
from .forms import VotePollForm, VoteOptionForm


# Create your views here.
def is_admin_or_manager(user):
    return user.is_authenticated and (
        user.role in ["admin", "manager"] or user.is_superuser
    )


# ---------- Admin: Create Poll ----------
@login_required
@user_passes_test(is_admin_or_manager)
def create_poll(request):
    if request.method == "POST":
        poll_form = VotePollForm(request.POST)
        if poll_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.created_by = request.user
            poll.save()
            messages.success(request, "Poll created! Add options below.")
            return redirect("votes:add_options", poll.id)
    else:
        poll_form = VotePollForm()
    return render(request, "votes/create_poll.html", {"poll_form": poll_form})


# ---------- Admin: Add Options ----------
@user_passes_test(is_admin_or_manager)
def add_options(request, poll_id):
    poll = get_object_or_404(VotePoll, id=poll_id)
    if request.method == "POST":
        form = VoteOptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.poll = poll
            option.save()
            messages.success(request, "Option added.")
            return redirect("votes:add_options", poll_id=poll.id)
    else:
        form = VoteOptionForm()

    return render(request, "votes/add_options.html", {"poll": poll, "form": form})


# ---------- Student: Vote ----------
@student_required
def cast_vote(request, poll_id):
    poll = get_object_or_404(VotePoll, id=poll_id)

    # Check if poll is expired
    if poll.is_expired():
        messages.warning(request, "This poll has ended. You cannot vote.")
        return redirect("votes:poll_results", poll_id=poll.id)

    # Check if student has already voted
    already_voted = Vote.objects.filter(poll=poll, voted_by=request.user).exists()
    if already_voted:
        messages.warning(request, "You have already voted in this poll.")
        return redirect("votes:poll_results", poll_id=poll.id)

    # Handle POST vote submission
    if request.method == "POST":
        option_id = request.POST.get("option")
        option = get_object_or_404(VoteOption, id=option_id, poll=poll)
        Vote.objects.create(poll=poll, option=option, voted_by=request.user)
        messages.success(request, "Your vote has been submitted successfully!")
        return redirect("votes:poll_results", poll_id=poll.id)

    # Render voting page
    options = poll.options.all()
    return render(request, "votes/cast_vote.html", {"poll": poll, "options": options})


# ---------- Anyone: View Results ----------
@login_required
def poll_results(request, poll_id):
    poll = get_object_or_404(VotePoll, id=poll_id)
    options = poll.options.all()
    total_votes = poll.total_votes()
    return render(
        request,
        "votes/poll_results.html",
        {
            "poll": poll,
            "options": options,
            "total_votes": total_votes,
            "is_expired": poll.is_expired(),
        },
    )

# ---------- Public Poll List ----------
@login_required
def poll_list(request):
    if request.user.role == "student":
        polls = [poll for poll in VotePoll.objects.all() if not poll.is_expired()]
    else:
        polls = VotePoll.objects.all()
    return render(request, "votes/poll_list.html", {"polls": polls})


@login_required
@user_passes_test(is_admin_or_manager)
def delete_poll(request, poll_id):
    poll = get_object_or_404(VotePoll, id=poll_id)

    if request.method == "POST":
        poll.delete()
        messages.success(request, "Poll deleted successfully.")
        return redirect("votes:poll_list")

    return render(request, "votes/confirm_delete_poll.html", {"poll": poll})
