from django import forms
from .models import PerformedProcedure
from clients.models import Client
from employees.models import Employee
from services.models import Service

class PerformedProcedureForm(forms.ModelForm):
    class Meta:
        model = PerformedProcedure
        fields = ['client', 'employee', 'service', 'date', 'price_at_moment']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'price_at_moment': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ограничим выбор только активными услугами
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        # можно добавить подсказки, но пока оставим