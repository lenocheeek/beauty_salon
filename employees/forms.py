from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['last_name', 'first_name', 'middle_name', 'specialization', 'user']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
        }