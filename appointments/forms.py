from django import forms
from .models import Appointment
from clients.models import Client
from employees.models import Employee
from services.models import Service

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'employee', 'service', 'date', 'time', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только активные услуги
        self.fields['service'].queryset = Service.objects.filter(is_active=True)