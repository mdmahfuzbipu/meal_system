from django import forms

class StudentMealPrefereceForm(forms.Form):
    prefers_beef = forms.BooleanField(required=False, label="I prefer Beef")
    prefers_fish = forms.BooleanField(required=False, label="I prefer Fish")