# students/serializers.py
from rest_framework import serializers
from .models import Complaint, DailyMealStatus, DailyMealCost, MonthlyMealSummary, Student, StudentDetails, StudentMealPreference, WeeklyMenu, WeeklyMenuReview


class DailyMealStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMealStatus
        fields = ["date", "breakfast_on", "lunch_on", "dinner_on"]


class DailyMealCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMealCost
        fields = ["date", "total_cost"]


class MonthlyMealSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyMealSummary
        fields = ["month", "total_on_days", "total_cost"]


class WeeklyMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyMenu
        fields = [
            "day_of_week",
            "breakfast_main",
            "lunch_main",
            "dinner_main",
            "lunch_alternate",
            "dinner_alternate",
        ]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["name", "room_number", "default_meal_status"]


class StudentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDetails
        fields = [
            "university_id",
            "department",
            "batch",
            "phone_number",
            "blood_group",
            "guardian_name",
            "guardian_phone",
        ]


class StudentMealPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMealPreference
        fields = ["month", "prefers_beef", "prefers_fish"]


class WeeklyMenuReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyMenuReview
        fields = ["day_of_week", "meal_type", "rating", "comment"]


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            "name",
            "room_number",
            "phone_number",
            "description",
            "is_fixed",
            "created_at",
        ]
