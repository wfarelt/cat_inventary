from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'ruc', 'address', 'phone', 'email', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full'}),
            'ruc': forms.TextInput(attrs={'class': 'w-full'}),
            'address': forms.TextInput(attrs={'class': 'w-full'}),
            'phone': forms.TextInput(attrs={'class': 'w-full'}),
            'email': forms.EmailInput(attrs={'class': 'w-full'}),
        }
