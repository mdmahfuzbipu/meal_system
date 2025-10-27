from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError

from students.models import (
    Student,
    StudentDetails,
    DEPARTMENT_CHOICES,
    BLOOD_GROUP_CHOICES,
)
from .models import CustomUser

class CustomUserCreationForm(AdminUserCreationForm): #AdminUserCreationForm new in Django 5.1 that removes the usable_pass error
    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")


UserModel = get_user_model()


class EmailOrUsernameAuthenticationForm(forms.Form):
    login = forms.CharField(label=_("Username or Email"), max_length=254)
    password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput)
    # captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    error_messages = {
        "invalid_login": _("Please enter a correct username/email and password."),
        "inactive": _("This account is inactive"),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        login = self.cleaned_data.get("login")
        password = self.cleaned_data.get("password")

        if login and password:
            user = None

            try:
                user_obj = UserModel.objects.get(
                    Q(email__iexact=login) | Q(username__iexact=login)
                )
                username = user_obj.get_username()

            except UserModel.DoesNotExist:
                username = login

            user = authenticate(self.request, username=username, password=password)

            if user is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )

            if not user.is_active:
                raise forms.ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )

            self.user_cache=user

        return self.cleaned_data

    def get_user(self):
        return self.user_cache
