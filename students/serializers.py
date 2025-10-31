# students/serializers.py
from rest_framework import serializers
from .models import DailyMealStatus, DailyMealCost, MonthlyMealSummary, WeeklyMenu


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
            "breakfast_alternate",
            "lunch_alternate",
            "dinner_alternate",
        ]
