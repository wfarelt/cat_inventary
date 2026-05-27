from django import forms
from .models import SiteConfiguration


class SiteConfigurationForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = ['key', 'value']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'w-full'}),
            'value': forms.Textarea(attrs={'class': 'w-full', 'rows': 4}),
        }
