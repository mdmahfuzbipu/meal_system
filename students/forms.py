from django import forms
from .models import StudentMealPreference, Complain

class StudentMealPreferenceForm(forms.ModelForm):
    class Meta:
        model = StudentMealPreference
        fields = ['prefers_beef', 'prefers_fish']
        labels = {
            'prefers_beef': 'Do you prefer Beef?',
            'prefers_fish': 'Do you prefer Fish?',
        }


class ComplainForm(forms.ModelForm):
    class Meta:
        model = Complain
        fields = ["name", "room_number", "phone", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
