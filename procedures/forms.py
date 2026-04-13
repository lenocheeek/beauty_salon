from django import forms
from .models import PerformedProcedure
from services.models import Service
from appointments.models import Appointment

class PerformedProcedureForm(forms.ModelForm):
    appointment = forms.ModelChoiceField(
        queryset=Appointment.objects.filter(status='scheduled'),
        required=False,
        label="Связать с предварительной записью",
        help_text="Выберите запись, если процедура была предварительно запланирована"
    )

    class Meta:
        model = PerformedProcedure
        fields = ['client', 'employee', 'service', 'date', 'price_at_moment']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'price_at_moment': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)