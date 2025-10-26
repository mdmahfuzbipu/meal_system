from django import forms
from django.utils import timezone
from .models import VotePoll, VoteOption


class VotePollForm(forms.ModelForm):
    class Meta:
        model = VotePoll
        fields = ["title", "question", "scope", "floor_number", "expires_at"]
        widgets = {
            "expires_at": forms.DateInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        scope = cleaned_data.get("scope")
        floor_number = cleaned_data.get("floor_number")

        if scope == "floor" and not floor_number:
            raise forms.ValidationError(
                "Please specify the floor number for a floor-specific poll."
            )
        return cleaned_data

    def clean_expires_at(self):
        expires_at = self.cleaned_data.get("expires_at")
        if expires_at and expires_at <= timezone.now():
            raise forms.ValidationError("Expiry date must be in the future.")
        return expires_at


class VoteOptionForm(forms.ModelForm):
    class Meta:
        model = VoteOption
        fields = ["option_text"]

    def clean_option_text(self):
        option_text = self.cleaned_data.get("option_text", "").strip()
        if not option_text:
            raise forms.ValidationError("Option text cannot be empty.")
        return option_text
