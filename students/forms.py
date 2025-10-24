from django import forms
from .models import StudentMealPreference

class StudentMealPreferenceForm(forms.ModelForm):
    class Meta:
        model = StudentMealPreference
        fields = ['prefers_beef', 'prefers_fish']
        labels = {
            'prefers_beef': 'Do you prefer Beef?',
            'prefers_fish': 'Do you prefer Fish?',
        }
