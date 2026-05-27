from django.db import models
from django.conf import settings
from django.utils import timezone


class MovementType(models.TextChoices):
    PURCHASE = 'PURCHASE', 'Purchase'
    SALE = 'SALE', 'Sale'
    ADJUSTMENT_IN = 'ADJUSTMENT_IN', 'Adjustment In'
    ADJUSTMENT_OUT = 'ADJUSTMENT_OUT', 'Adjustment Out'
    CUSTOMER_RETURN = 'CUSTOMER_RETURN', 'Customer Return'
    SUPPLIER_RETURN = 'SUPPLIER_RETURN', 'Supplier Return'
    INITIAL_STOCK = 'INITIAL_STOCK', 'Initial Stock'
    MANUAL_CORRECTION = 'MANUAL_CORRECTION', 'Manual Correction'


class StockMovement(models.Model):
    from products.models import Product

    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='movements')
    movement_type = models.CharField(max_length=30, choices=MovementType.choices, db_index=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    previous_stock = models.DecimalField(max_digits=12, decimal_places=2)
    new_stock = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reason = models.CharField(max_length=255)
    reference = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.product} {self.movement_type} {self.quantity} -> {self.new_stock}"


class CostSource(models.TextChoices):
    PURCHASE = 'PURCHASE', 'Purchase'
    MANUAL = 'MANUAL', 'Manual'
    IMPORT = 'IMPORT', 'Import'


class ProductCostHistory(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='cost_history')
    previous_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_cost = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=20, choices=CostSource.choices, default=CostSource.MANUAL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Product Cost History'
        verbose_name_plural = 'Product Cost History'
        indexes = [models.Index(fields=['product']), models.Index(fields=['created_at'])]

    def __str__(self):
        return f"{self.product} cost {self.previous_cost} -> {self.new_cost} ({self.source})"


class ProductPriceHistory(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='price_history')
    previous_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Product Price History'
        verbose_name_plural = 'Product Price History'
        indexes = [models.Index(fields=['product']), models.Index(fields=['created_at'])]

    def __str__(self):
        return f"{self.product} price {self.previous_price} -> {self.new_price}"
