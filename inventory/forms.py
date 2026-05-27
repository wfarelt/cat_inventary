from decimal import Decimal
from django import forms

from .models import StockMovement, ProductCostHistory, ProductPriceHistory


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = '__all__'

    def clean_quantity(self):
        q = self.cleaned_data.get('quantity')
        if q is None:
            raise forms.ValidationError('Quantity is required')
        try:
            q = Decimal(q)
        except Exception:
            raise forms.ValidationError('Invalid quantity')
        if q <= 0:
            raise forms.ValidationError('Quantity must be positive')
        return q

    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if not reason:
            raise forms.ValidationError('Reason obligatorio')
        return reason


class ProductCostHistoryForm(forms.ModelForm):
    class Meta:
        model = ProductCostHistory
        fields = '__all__'

    def clean_new_cost(self):
        nc = self.cleaned_data.get('new_cost')
        if nc is None:
            raise forms.ValidationError('New cost is required')
        try:
            nc = Decimal(nc)
        except Exception:
            raise forms.ValidationError('Invalid cost')
        return nc


class ProductPriceHistoryForm(forms.ModelForm):
    class Meta:
        model = ProductPriceHistory
        fields = '__all__'

    def clean_new_price(self):
        np = self.cleaned_data.get('new_price')
        if np is None:
            raise forms.ValidationError('New price is required')
        try:
            np = Decimal(np)
        except Exception:
            raise forms.ValidationError('Invalid price')
        return np
