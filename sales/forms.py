from decimal import Decimal
from django import forms
from django.forms import inlineformset_factory

from .models import Sale, SaleItem, Customer


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'status', 'sale_date', 'payment_type', 'due_date', 'notes', 'discount']
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SaleItemForm(forms.ModelForm):
    product_search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Código o descripción', 'class': 'product-autocomplete'}))

    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'class': 'qty-input'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'price-input'}),
        }


SaleItemFormSet = inlineformset_factory(Sale, SaleItem, form=SaleItemForm, extra=5, can_delete=True)


class QuickCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone']
