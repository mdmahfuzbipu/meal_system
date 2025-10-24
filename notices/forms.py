from django import forms
from .models import Notice


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ["title", "message", "image", "visible_to_students"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Notice Title"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Enter notice details...",
                }
            ),
        }