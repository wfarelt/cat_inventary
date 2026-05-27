from decimal import Decimal
from django import forms

from .models import Purchase, PurchaseItem, Supplier


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ('supplier', 'invoice_number', 'invoice_date', 'purchase_date', 'discount', 'notes')

    def clean_supplier(self):
        sup = self.cleaned_data.get('supplier')
        if not sup:
            raise forms.ValidationError('Supplier obligatorio')
        return sup


class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ('product', 'quantity', 'unit_cost')

    def clean_quantity(self):
        q = self.cleaned_data.get('quantity')
        try:
            q = Decimal(q)
        except Exception:
            raise forms.ValidationError('Cantidad inválida')
        if q <= 0:
            raise forms.ValidationError('Cantidad debe ser mayor que cero')
        return q

    def clean_unit_cost(self):
        c = self.cleaned_data.get('unit_cost')
        try:
            c = Decimal(c)
        except Exception:
            raise forms.ValidationError('Costo inválido')
        if c <= 0:
            raise forms.ValidationError('Costo debe ser mayor que cero')
        return c
