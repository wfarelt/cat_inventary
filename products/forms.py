from django import forms
from .models import Brand, Category, Product, ProductKit, ProductKitItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción (opcional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('El nombre de la categoría no puede estar vacío.')
        
        # Verificar duplicado (excluir la instancia actual si es edición)
        qs = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una categoría con este nombre.')
        
        return name


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'description', 'cross_reference', 'category', 'brand_ref', 'cost', 'price', 'stock', 'stock_reserved', 'stock_min', 'location', 'image', 'notes', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand_ref': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand_ref'].queryset = Brand.objects.filter(is_active=True).order_by('name')


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la marca'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción (opcional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('El nombre de la marca no puede estar vacío.')

        qs = Brand.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una marca con este nombre.')

        return name


class ProductKitForm(forms.ModelForm):
    class Meta:
        model = ProductKit
        fields = ['name', 'description', 'is_active']


class ProductKitItemForm(forms.ModelForm):
    class Meta:
        model = ProductKitItem
        fields = ['product', 'quantity']
