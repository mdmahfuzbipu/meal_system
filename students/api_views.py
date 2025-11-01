from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date
from .models import Complaint, DailyMealStatus, DailyMealCost, MonthlyMealSummary, StudentDetails, StudentMealPreference, WeeklyMenu, WeeklyMenuReview
from .serializers import (
    ComplaintSerializer,
    DailyMealStatusSerializer,
    DailyMealCostSerializer,
    MonthlyMealSummarySerializer,
    StudentDetailsSerializer,
    StudentMealPreferenceSerializer,
    StudentSerializer,
    WeeklyMenuReviewSerializer,
    WeeklyMenuSerializer,
)
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def today_menu(request):
    today_weekday = date.today().strftime("%A")
    menu = WeeklyMenu.objects.filter(day_of_week=today_weekday).first()
    if menu:
        serializer = WeeklyMenuSerializer(menu)
        return Response(serializer.data)
    return Response({"detail": "No menu set for today."}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def today_meal_status(request):
    student = request.user.student
    status = DailyMealStatus.objects.filter(student=student, date=date.today()).first()
    if status:
        serializer = DailyMealStatusSerializer(status)
        return Response(serializer.data)
    return Response({"detail": "No meal status for today."}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def today_meal_cost(request):
    student = request.user.student
    cost = DailyMealCost.objects.filter(student=student, date=date.today()).first()
    if cost:
        serializer = DailyMealCostSerializer(cost)
        return Response(serializer.data)
    return Response({"detail": "No meal cost for today."}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_summary(request):
    student = request.user.student
    summary = (
        MonthlyMealSummary.objects.filter(student=student).order_by("-month").first()
    )
    if summary:
        serializer = MonthlyMealSummarySerializer(summary)
        return Response(serializer.data)
    return Response({"detail": "No monthly summary available."}, status=404)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def today_meal_review(request):
    student = request.user.student
    today_weekday = date.today().strftime("%A")

    if request.method == "GET":
        reviews = WeeklyMenuReview.objects.filter(
            student=student, day_of_week=today_weekday
        )
        serializer = WeeklyMenuReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = WeeklyMenuReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student, day_of_week=today_weekday)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_complaints(request):
    student = request.user.student
    complaints = Complaint.objects.filter(student=student).order_by("-created_at")
    serializer = ComplaintSerializer(complaints, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_profile(request):
    student = request.user.student
    student_data = StudentSerializer(student).data
    details = StudentDetails.objects.filter(student=student).first()
    details_data = StudentDetailsSerializer(details).data if details else {}
    pref = (
        StudentMealPreference.objects.filter(student=student).order_by("-month").first()
    )
    pref_data = StudentMealPreferenceSerializer(pref).data if pref else {}

    return Response(
        {
            "student": student_data,
            "details": details_data,
            "meal_preference": pref_data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def today_notices(request):
    return Response({"notices": ["No new notices today. Enjoy your meal!"]})
