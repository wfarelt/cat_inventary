from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel
from decimal import Decimal


class PurchaseStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=200, db_index=True)
    phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return self.name


class Purchase(TimeStampedModel):
    supplier = models.ForeignKey('purchases.Supplier', on_delete=models.PROTECT, related_name='purchases')
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateField(default=timezone.now, db_index=True)
    status = models.CharField(max_length=20, choices=PurchaseStatus.choices, default=PurchaseStatus.DRAFT, db_index=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'
        indexes = [models.Index(fields=['purchase_date']), models.Index(fields=['status'])]

    def __str__(self):
        return f"{self.pk or ''} - {self.supplier.name} - {self.purchase_date}"

    @property
    def can_edit(self):
        return self.status == PurchaseStatus.DRAFT

    @property
    def can_cancel(self):
        return self.status == PurchaseStatus.CONFIRMED

    def recalc_totals(self):
        items = self.items.all()
        subtotal = Decimal('0.00')
        for it in items:
            subtotal += (it.subtotal or Decimal('0.00'))
        self.subtotal = subtotal
        self.total = subtotal - (self.discount or Decimal('0.00'))
        return self.subtotal, self.total


class PurchaseItem(models.Model):
    purchase = models.ForeignKey('purchases.Purchase', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='purchase_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = 'Purchase Item'
        verbose_name_plural = 'Purchase Items'
        unique_together = ('purchase', 'product')

    def __str__(self):
        return f"{self.purchase_id} - {self.product.code} x {self.quantity}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if (self.quantity is None) or (Decimal(self.quantity) <= 0):
            raise ValidationError('Quantity must be greater than zero')
        if (self.unit_cost is None) or (Decimal(self.unit_cost) <= 0):
            raise ValidationError('Unit cost must be greater than zero')

    def save(self, *args, **kwargs):
        # compute subtotal
        try:
            q = Decimal(self.quantity or 0)
            uc = Decimal(self.unit_cost or 0)
        except Exception:
            q = Decimal('0')
            uc = Decimal('0')
        self.subtotal = q * uc
        super().save(*args, **kwargs)



class PurchaseAudit(models.Model):
    EVENT_CHOICES = [
        ('CREATED', 'Created'),
        ('EDITED', 'Edited'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COST_UPDATED', 'Cost Updated'),
        ('OTHER', 'Other'),
    ]
    purchase = models.ForeignKey('purchases.Purchase', on_delete=models.CASCADE, related_name='audits')
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(null=True, blank=True)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Purchase Audit'
        verbose_name_plural = 'Purchase Audits'
        indexes = [models.Index(fields=['purchase']), models.Index(fields=['event']), models.Index(fields=['created_at'])]

    def __str__(self):
        return f"{self.purchase_id} {self.event} @ {self.created_at}"
