from django import forms
from .models import Employee, DayOff

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['last_name', 'first_name', 'middle_name', 'specialization', 'user']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
        }

class DayOffForm(forms.ModelForm):
    class Meta:
        model = DayOff
        fields = ['date', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.TextInput(attrs={'placeholder': 'Причина (необязательно)'}),
        }