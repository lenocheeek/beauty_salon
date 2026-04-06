from django import forms
from services.models import Category

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="С даты",
        required=False
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="По дату",
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Категория",
        required=False,
        empty_label="Все категории"
    )