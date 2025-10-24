from django import forms
from .models import StudentMealPreference, WeeklyMenuReview

class StudentMealPreferenceForm(forms.ModelForm):
    class Meta:
        model = StudentMealPreference
        fields = ['prefers_beef', 'prefers_fish']
        labels = {
            'prefers_beef': 'Do you prefer Beef?',
            'prefers_fish': 'Do you prefer Fish?',
        }


class WeeklyMenuReviewForm(forms.ModelForm):
    class Meta:
        model = WeeklyMenuReview
        fields = ["day_of_week", "meal_type", "rating", "comment"]
        widgets = {
            "day_of_week": forms.Select(attrs={"class": "form-select"}),
            "meal_type": forms.Select(attrs={"class": "form-select"}),
            "rating": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"rows": 4, "class": "form-textarea"}),
        }
