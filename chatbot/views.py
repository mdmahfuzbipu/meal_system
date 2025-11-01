from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.test import APIRequestFactory, force_authenticate
from meal_system import settings
import logging

from .ai_utils import gemini_generate


from students.models import (
    Student,
    DailyMealStatus,
    DailyMealCost,
    MonthlyMealSummary,
    WeeklyMenu,
)

# API Views (for live data)
from students.api_views import (
    today_menu,
    today_meal_status,
    today_meal_cost,
    monthly_summary,
    student_profile,
    my_complaints,
    today_notices,
)
from notices.models import Notice

logger = logging.getLogger(__name__)


#  Chatbot Page View
# -----------------------------
@login_required
def chat_page(request):
    """Render the chatbot interface page."""
    return render(request, "chatbot/chat.html", {"page_title": "Student Chat Assistant"})


# -----------------------------
#  Main Chat API View
# -----------------------------
@login_required
def chat_api(request):
    user_message = request.GET.get("message", "").strip().lower()
    user = request.user
    student_name = getattr(getattr(user, "student", None), "name", user.username)

    reply = None
    factory = APIRequestFactory()

    try:
        # --- Basic greetings ---
        if any(word in user_message for word in ["hi", "hello", "hey"]):
            reply = (
                f"👋 Hello {student_name}! How can I assist you today? "
                "You can ask about today's menu, meal status, cost, or monthly summary."
            )

        elif "help" in user_message:
            reply = (
                " Here are some things I can help you with:<br>"
                "- 'What's today's menu?'<br>"
                "- 'Show my meal status'<br>"
                "- 'How much did I spend this month?'<br>"
                "- 'Show my profile'<br>"
                "- 'Any new notices?'<br>"
                "- 'My complaints'<br>"
                "- Or just chat with me naturally!"
            )

        # --- Menu ---
        elif "menu" in user_message:
            api_req = factory.get("/api/menu/today/")
            force_authenticate(api_req, user=user)
            response = today_menu(api_req)
            if response.status_code == 200 and isinstance(response.data, dict):
                data = response.data
                reply = (
                    f"🍽️ Today's Menu ({data.get('day_of_week', 'N/A')}):<br>"
                    f"Breakfast: {data.get('breakfast_main', 'N/A')}<br>"
                    f"Lunch: {data.get('lunch_main', 'N/A')}<br>"
                    f"Dinner: {data.get('dinner_main', 'N/A')}"
                )
            else:
                reply = "🍽️ Sorry, today's menu is not set yet. Please ask the manager to update it."

        # --- Meal status ---
        elif "status" in user_message:
            api_req = factory.get("/api/meal-status/today/")
            force_authenticate(api_req, user=user)
            response = today_meal_status(api_req)
            if response.status_code == 200:
                data = response.data
                reply = (
                    f"📅 Meal Status for {data['date']}:<br>"
                    f"Breakfast: {'ON' if data['breakfast_on'] else 'OFF'}<br>"
                    f"Lunch: {'ON' if data['lunch_on'] else 'OFF'}<br>"
                    f"Dinner: {'ON' if data['dinner_on'] else 'OFF'}"
                )
            else:
                reply = "⚠️ No meal status found for today."

        # --- Today's cost ---
        elif "cost" in user_message and "today" in user_message:
            api_req = factory.get("/api/meal-cost/today/")
            force_authenticate(api_req, user=user)
            response = today_meal_cost(api_req)
            if response.status_code == 200:
                data = response.data
                reply = f"💰 Today's total meal cost is {data['total_cost']} Taka."
            else:
                reply = "⚠️ No meal cost record found for today."

        # --- Monthly summary ---
        elif any(k in user_message for k in ["cost", "spend", "summary"]):
            api_req = factory.get("/api/monthly-summary/")
            force_authenticate(api_req, user=user)
            response = monthly_summary(api_req)
            if response.status_code == 200:
                data = response.data
                reply = (
                    f"📊 Monthly Summary ({data['month']}):<br>"
                    f"Total ON Days: {data['total_on_days']}<br>"
                    f"Total Cost: {data['total_cost']} Taka"
                )
            else:
                reply = "⚠️ No monthly summary available yet."

        # --- Student profile ---
        elif "profile" in user_message:
            api_req = factory.get("/api/student/profile/")
            force_authenticate(api_req, user=user)
            response = student_profile(api_req)
            if response.status_code == 200:
                data = response.data
                student = data["student"]
                details = data["details"]
                reply = (
                    f"👤 Profile Info:<br>"
                    f"Name: {student['name']}<br>"
                    f"Room: {student['room_number']}<br>"
                    f"Department: {details.get('department', 'N/A')}<br>"
                    f"Phone: {details.get('phone_number', 'N/A')}"
                )
            else:
                reply = "⚠️ Couldn't retrieve your profile details."

        # --- Complaints ---
        elif "complaint" in user_message:
            api_req = factory.get("/api/complaints/my/")
            force_authenticate(api_req, user=user)
            response = my_complaints(api_req)
            if response.status_code == 200 and response.data:
                data = response.data[0]
                reply = (
                    f"🛠️ Your latest complaint:<br>"
                    f"{data['description']}<br>"
                    f"Status: {'Fixed ✅' if data['is_fixed'] else 'Pending ⏳'}"
                )
            else:
                reply = "✅ You have no active complaints."

        # --- Notices ---
        elif "notice" in user_message:
            api_req = factory.get("/api/notices/today/")
            force_authenticate(api_req, user=user)
            response = today_notices(api_req)
            if response.status_code == 200 and response.data.get("notices"):
                notices = "<br>".join([f"📢 {n}" for n in response.data["notices"]])
                reply = notices
            else:
                reply = "📢 No new notices today."

## ---------------- AI fallback using Gemini ----------------------
        if not reply:
            # Collect live context for AI
            context_data = {}
            for view_func, key in [
                (today_menu, "today_menu"),
                (today_meal_status, "meal_status"),
                (today_meal_cost, "today_cost"),
                (monthly_summary, "monthly_summary"),
                (student_profile, "student_profile"),
            ]:
                api_req = factory.get("/dummy/")
                force_authenticate(api_req, user=user)
                resp = view_func(api_req)
                if resp.status_code == 200:
                    context_data[key] = resp.data

            # AI prompt
            ai_prompt = (
                f"You are a smart and polite hostel meal assistant chatbot.\n"
                f"Student: {student_name}\n\n"
                f"Context data (JSON): {context_data}\n\n"
                f"User question: {user_message}\n\n"
                "Give a helpful, short and friendly answer using the provided context if relevant."
            )

            reply = gemini_generate(
                ai_prompt, model_name="gemini-2.0-flash", temperature=0.4
            )

    except Exception as e:
        logger.exception("Chat API failed")
        reply = "⚠️ Sorry, something went wrong while processing your request."

    if not reply:
        reply = "🤖 Sorry, I couldn’t understand that. Try asking about 'menu', 'status', or 'monthly summary'."

    return JsonResponse({"reply": reply})





    # ------------------------OpenAI API---------------

    #         try:
    #             gpt_response = openai.ChatCompletion.create(
    #                 model="gpt-4o-mini",
    #                 messages=[{"role": "user", "content": prompt}],
    #                 max_tokens=200,
    #             )
    #             reply = gpt_response.choices[0].message.content.strip()
    #         except Exception as e:
    #             reply = "⚠️ AI system is currently unavailable. Please try again later."

    # except Exception as e:
    #     reply = "⚠️ Sorry, something went wrong while processing your request."

    # return JsonResponse({"reply": reply})
