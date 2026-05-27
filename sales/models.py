from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel


class SaleStatus(models.TextChoices):
    PROFORMA = 'PROFORMA', 'Proforma'
    RESERVA = 'RESERVA', 'Reserva'
    PEDIDO = 'PEDIDO', 'Pedido'
    EJECUTADO = 'EJECUTADO', 'Ejecutado'
    ANULADO = 'ANULADO', 'Anulado'


class PaymentType(models.TextChoices):
    CASH = 'CASH', 'Cash'
    CREDIT = 'CREDIT', 'Credit'


class Customer(TimeStampedModel):
    name = models.CharField(max_length=200, db_index=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name


class Sale(TimeStampedModel):
    number = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    customer = models.ForeignKey('sales.Customer', on_delete=models.PROTECT, related_name='sales')
    status = models.CharField(max_length=20, choices=SaleStatus.choices, default=SaleStatus.PROFORMA, db_index=True)
    sale_date = models.DateField(default=timezone.now, db_index=True)
    expiration_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pending_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices, default=PaymentType.CASH)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'
        indexes = [models.Index(fields=['number']), models.Index(fields=['sale_date']), models.Index(fields=['status'])]

    def __str__(self):
        return f"{self.number or ''} - {self.customer.name} - {self.sale_date}"

    def recalc_totals(self):
        items = self.items.all()
        subtotal = Decimal('0.00')
        for it in items:
            subtotal += (it.subtotal or Decimal('0.00'))
        self.subtotal = subtotal
        self.total = subtotal - (self.discount or Decimal('0.00'))
        self.pending_amount = self.total - (self.paid_amount or Decimal('0.00'))
        return self.subtotal, self.total

    @property
    def is_paid(self):
        return (self.total or Decimal('0.00')) <= (self.paid_amount or Decimal('0.00'))

    @property
    def can_edit(self):
        return self.status in (SaleStatus.PROFORMA, SaleStatus.RESERVA, SaleStatus.PEDIDO)

    def save(self, *args, **kwargs):
        # ensure totals are coherent
        if self.total is None:
            self.total = Decimal('0.00')
        if self.subtotal is None:
            self.subtotal = Decimal('0.00')

        # First save to obtain pk if number generation is needed
        if not self.number:
            super().save(*args, **kwargs)
            self.number = str(self.pk).zfill(6)
            super().save(update_fields=['number'])
            return

        super().save(*args, **kwargs)


class SaleItem(models.Model):
    sale = models.ForeignKey('sales.Sale', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'

    def __str__(self):
        return f"{self.sale_id} - {self.product.code} x {self.quantity}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if (self.quantity is None) or (Decimal(self.quantity) <= 0):
            raise ValidationError('Quantity must be greater than zero')
        if (self.unit_price is None) or (Decimal(self.unit_price) < 0):
            raise ValidationError('Unit price must be zero or greater')

    def save(self, *args, **kwargs):
        try:
            q = Decimal(self.quantity or 0)
            up = Decimal(self.unit_price or 0)
        except Exception:
            q = Decimal('0')
            up = Decimal('0')
        self.subtotal = q * up
        super().save(*args, **kwargs)


class SalePayment(models.Model):
    sale = models.ForeignKey('sales.Sale', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Sale Payment'
        verbose_name_plural = 'Sale Payments'

    def __str__(self):
        return f"{self.sale.number or self.sale_id} - {self.amount}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            # update sale aggregates
            sale = self.sale
            paid = sale.payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            sale.paid_amount = paid
            sale.pending_amount = (sale.total or Decimal('0.00')) - paid
            sale.save(update_fields=['paid_amount', 'pending_amount'])


class SaleAudit(models.Model):
    EVENT_CHOICES = [
        ('CREATED', 'Created'),
        ('EXECUTED', 'Executed'),
        ('CANCELLED', 'Cancelled'),
        ('PAYMENT', 'Payment'),
        ('RESERVED', 'Reserved'),
        ('RELEASED', 'Released'),
        ('PRICE_CHANGED', 'Price Changed'),
        ('OTHER', 'Other'),
    ]
    sale = models.ForeignKey('sales.Sale', on_delete=models.CASCADE, related_name='audits')
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(null=True, blank=True)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Sale Audit'
        verbose_name_plural = 'Sale Audits'

    def __str__(self):
        return f"{self.sale_id} {self.event} @ {self.created_at}"
