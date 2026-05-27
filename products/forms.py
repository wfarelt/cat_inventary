from django import forms
from .models import Category, Product, ProductKit, ProductKitItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'description', 'cross_reference', 'category', 'brand', 'cost', 'price', 'stock', 'stock_reserved', 'stock_min', 'location', 'image', 'notes', 'is_active']


class ProductKitForm(forms.ModelForm):
    class Meta:
        model = ProductKit
        fields = ['name', 'description', 'is_active']


class ProductKitItemForm(forms.ModelForm):
    class Meta:
        model = ProductKitItem
        fields = ['product', 'quantity']
