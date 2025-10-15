from django import forms
from django.contrib.auth import get_user_model

from .models import WeeklyMenuProposal, ManagerProfile


User = get_user_model()


class ManagerRegistrationForm(forms.ModelForm):
    
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = ManagerProfile
        fields = ["nid", "address", "emergency_phone", "phone_number"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def clean_nid(self):
        nid = self.cleaned_data["nid"]
        if ManagerProfile.objects.filter(nid=nid).exists():
            raise forms.ValidationError("A manager with this NID already exists.")
        return nid

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = User.objects.create_user(
            email=cleaned_data["email"],
            password=cleaned_data["password"],
            role="manager",
        )
        manager = super().save(commit=False)
        manager.user = user
        if commit:
            manager.save()
        return manager


class WeeklyMenuProposalForm(forms.ModelForm):
    class Meta:
        model = WeeklyMenuProposal
        fields = [
            "day_of_week",
            "breakfast_main",
            "breakfast_cost",
            "lunch_main",
            "lunch_cost",
            "lunch_contains_beef",
            "lunch_contains_fish",
            "lunch_alternate",
            "lunch_cost_alternate",
            "dinner_main",
            "dinner_cost",
            "dinner_contains_beef",
            "dinner_contains_fish",
            "dinner_alternate",
            "dinner_cost_alternate",
        ]
        widgets = {
            "day_of_week": forms.HiddenInput(),  
            "breakfast_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "lunch_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "lunch_cost_alternate": forms.NumberInput(
                attrs={"step": "0.01", "min": "0"}
            ),
            "dinner_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "dinner_cost_alternate": forms.NumberInput(
                attrs={"step": "0.01", "min": "0"}
            ),
        }
