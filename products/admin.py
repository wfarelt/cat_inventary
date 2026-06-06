from django.contrib import admin
from .models import Brand, Category, Product, ProductKit, ProductKitItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)


class ProductKitItemInline(admin.TabularInline):
    model = ProductKitItem
    extra = 1


@admin.register(ProductKit)
class ProductKitAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    inlines = [ProductKitItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'brand_display', 'category', 'price', 'stock', 'stock_reserved', 'available_stock', 'is_active')
    search_fields = ('code', 'description', 'cross_reference')
    list_filter = ('category', 'brand_ref', 'is_active')
    readonly_fields = ('available_stock',)

    @admin.display(description='Marca')
    def brand_display(self, obj):
        return obj.brand_ref.name if obj.brand_ref else obj.brand
