from django import forms
from .models import PaymentSlip, StudentMealPreference, WeeklyMenuReview

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


class PaymentSlipForm(forms.ModelForm):
    class Meta:
        model = PaymentSlip
        fields = [
            "month",
            "amount",
            "transaction_id",
            "account_number",
            "slip_image",
            "info",
        ]
        widgets = {
            "month": forms.TextInput(attrs={"type": "month"}),
            "amount": forms.NumberInput(attrs={"step": "100"}),
            "info": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Add any notes or references here"}
            ),
        }
        help_texts = {
            "info": "Add any notes, payment reference, or additional info for the admin.",
        }
