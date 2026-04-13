from django import forms
from .models import Appointment
from services.models import Service
from employees.models import DayOff

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
        self.fields['service'].queryset = Service.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        date = cleaned_data.get('date')

        if employee and date:
            if DayOff.objects.filter(employee=employee, date=date).exists():
                raise forms.ValidationError(f"Сотрудник {employee} не работает в выбранную дату (выходной день).")

        return cleaned_data