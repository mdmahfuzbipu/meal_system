from django.db import transaction
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from students.models import (
    Student,
    StudentDetails,
    DEPARTMENT_CHOICES,
    BLOOD_GROUP_CHOICES,
)

User = get_user_model()


class StudentRegistrationForm(forms.ModelForm):
    # User fields
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=True
    )
    password2 = forms.CharField(
        label="Confirm password", widget=forms.PasswordInput, required=True
    )

    # Student fields (minimal set to start)
    name = forms.CharField(max_length=40, required=True)
    room_number = forms.CharField(max_length=5, required=True)

    # Meal preferences
    default_prefers_beef = forms.BooleanField(
        label="Prefers Beef", required=False, initial=True
    )
    default_prefers_fish = forms.BooleanField(
        label="Prefers Fish", required=False, initial=True
    )

    # StudentDetails fields
    university_id = forms.CharField(max_length=20, required=True)
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=True)
    batch = forms.CharField(max_length=4, required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=True
    )
    national_id = forms.CharField(max_length=20, required=True)
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=True)
    phone_number = forms.CharField(max_length=16, required=True)
    guardian_name = forms.CharField(max_length=40, required=True)
    guardian_phone = forms.CharField(max_length=16, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if not p1 or not p2 or p1 != p2:
            raise ValidationError("Passwords don't match.")
        return p2

    def clean_university_id(self):
        uid = self.cleaned_data.get("university_id")
        if StudentDetails.objects.filter(university_id=uid).exists():
            raise ValidationError("A student with this university ID already exists.")
        return uid

    def clean_national_id(self):
        nid = self.cleaned_data.get("national_id")
        if StudentDetails.objects.filter(national_id=nid).exists():
            raise ValidationError("A student with this national ID already exists.")
        return nid

    @transaction.atomic
    def save(self, commit=True):
        # Create user
        user = User(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
        )
        user.set_password(self.cleaned_data["password1"])
        # force role to student
        try:
            user.role = "student"
        except Exception:
            pass

        if commit:
            user.save()

            # create Student
            student = Student.objects.create(
                user=user,
                name=self.cleaned_data["name"],
                room_number=self.cleaned_data["room_number"],
                default_meal_status=True,
                default_prefers_beef=self.cleaned_data.get(
                    "default_prefers_beef", True
                ),
                default_prefers_fish=self.cleaned_data.get(
                    "default_prefers_fish", True
                ),
            )

            # create StudentDetails
            StudentDetails.objects.create(
                student=student,
                university_id=self.cleaned_data["university_id"],
                department=self.cleaned_data["department"],
                batch=self.cleaned_data["batch"],
                date_of_birth=self.cleaned_data["date_of_birth"],
                national_id=self.cleaned_data["national_id"],
                address="",
                phone_number=self.cleaned_data["phone_number"],
                blood_group=self.cleaned_data["blood_group"],
                guardian_name=self.cleaned_data["guardian_name"],
                guardian_phone=self.cleaned_data["guardian_phone"],
                profile_picture=self.cleaned_data.get("profile_picture"),
            )

        return user
