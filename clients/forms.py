from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['last_name', 'first_name', 'middle_name', 'phone', 'email', 'birth_date', 'discount_percentage']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'discount_percentage': forms.NumberInput(attrs={'step': '0.01'}),
        }