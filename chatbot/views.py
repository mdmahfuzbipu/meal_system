from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import date
from students.models import (
    Student,
    DailyMealStatus,
    DailyMealCost,
    MonthlyMealSummary,
    WeeklyMenu,
)
from notices.models import Notice


@login_required
def chat_page(request):
    """Render the chatbot interface page."""
    return render(
        request, "chatbot/chat.html", {"page_title": "Student Chat Assistant"}
    )


@login_required
def chat_api(request):
    """Handle chatbot message responses."""
    user_message = request.GET.get("message", "").strip().lower()
    student = request.user.student
    today = date.today()
    reply = "🤖 Sorry, I didn’t understand that. Try asking about your today's menu, today's cost, monthly summary or notices."

    # Greeting
    if any(word in user_message for word in ["hi", "hello", "hey"]):
        reply = f"Hello {student.name}! 👋 How can I help you today?"

    # Meal status (ON/OFF)
    elif "meal" in user_message and "status" in user_message:
        today_status = DailyMealStatus.objects.filter(
            student=student, date=today
        ).first()
        if today_status:
            reply = (
                f"🍽️ Your meal status for today ({today}):\n"
                f"Breakfast: {'ON' if today_status.breakfast_on else 'OFF'} | "
                f"Lunch: {'ON' if today_status.lunch_on else 'OFF'} | "
                f"Dinner: {'ON' if today_status.dinner_on else 'OFF'}"
            )
        else:
            reply = "No meal status found for today."

    # Today's menu
    elif "menu" in user_message or "today" in user_message and "menu" in user_message:
        weekday = today.strftime("%A")
        menu = WeeklyMenu.objects.filter(day_of_week=weekday).first()
        if menu:
            reply = (
                f"🍛 Today’s Menu ({weekday}):\n"
                f"Breakfast: {menu.breakfast_main}\n"
                f"Lunch: {menu.lunch_main}\n"
                f"Dinner: {menu.dinner_main}"
            )
        else:
            reply = f"No menu set for {weekday} yet."

    # Today's meal cost
    elif "today" in user_message and "cost" in user_message:
        cost_obj = DailyMealCost.objects.filter(student=student, date=today).first()
        if cost_obj:
            reply = f"💰 Your total meal cost for today ({today}) is {cost_obj.total_cost} BDT."
        else:
            reply = "No meal cost record found for today."

    # Monthly summary
    elif "summary" in user_message and "monthly" in user_message:
        summary = (
            MonthlyMealSummary.objects.filter(student=student)
            .order_by("-month")
            .first()
        )
        if summary:
            reply = (
                f"📊 Monthly Summary for {summary.month}:\n"
                f"Total ON Days: {summary.total_on_days}\n"
                f"Total Cost: {summary.total_cost} BDT"
            )
        else:
            reply = "No monthly summary available yet."

    # Monthly cost
    elif "cost" in user_message and "meal" in user_message:
        summary = (
            MonthlyMealSummary.objects.filter(student=student)
            .order_by("-month")
            .first()
        )
        if summary:
            reply = f"💰 Your total meal cost for {summary.month} is {summary.total_cost} BDT."
        else:
            reply = "No monthly cost record found."

    # Latest notices
    elif (
        "notice" in user_message
        or "update" in user_message
        or "announcement" in user_message
    ):
        notices = Notice.objects.order_by("-created_at")[:3]
        if notices.exists():
            formatted = "\n".join([f"📢 {n.title}" for n in notices])
            reply = "Here are the latest notices:\n" + formatted
        else:
            reply = "No new notices at the moment."

    # Help command
    elif "help" in user_message:
        reply = (
            "🧭 You can ask me things like:\n"
            "- 'What is my meal status?'\n"
            "- 'Show today's menu'\n"
            "- 'Today's cost'\n"
            "- 'Monthly summary'\n"
            "- 'Latest notices'\n"
        )

    return JsonResponse({"reply": reply})
