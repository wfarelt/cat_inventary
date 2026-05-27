from django.contrib import admin
from django.utils.html import format_html

from .models import StockMovement, ProductCostHistory, ProductPriceHistory
from .forms import StockMovementForm, ProductCostHistoryForm, ProductPriceHistoryForm


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    form = StockMovementForm
    list_display = ('product', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'unit_cost', 'reason', 'reference', 'created_by', 'created_at')
    search_fields = ('product__code', 'product__description', 'reason', 'reference')
    list_filter = ('movement_type', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(ProductCostHistory)
class ProductCostHistoryAdmin(admin.ModelAdmin):
    form = ProductCostHistoryForm
    list_display = ('product', 'previous_cost', 'new_cost', 'source', 'created_by', 'created_at')
    search_fields = ('product__code', 'product__description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    form = ProductPriceHistoryForm
    list_display = ('product', 'previous_price', 'new_price', 'created_by', 'created_at')
    search_fields = ('product__code', 'product__description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
