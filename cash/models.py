from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel


class CashStatus(models.TextChoices):
    OPEN = 'OPEN', 'Open'
    CLOSED = 'CLOSED', 'Closed'


class CashMovementType(models.TextChoices):
    SALE_PAYMENT = 'SALE_PAYMENT', 'Sale Payment'
    EXPENSE = 'EXPENSE', 'Expense'
    MANUAL_IN = 'MANUAL_IN', 'Manual In'
    MANUAL_OUT = 'MANUAL_OUT', 'Manual Out'


class CashOpening(models.Model):
    opening_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    opened_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=CashStatus.choices, default=CashStatus.OPEN, db_index=True)

    class Meta:
        verbose_name = 'Cash Opening'
        verbose_name_plural = 'Cash Openings'

    def __str__(self):
        return f"Opening @ {self.opened_at} ({self.opening_amount})"


class CashMovement(models.Model):
    movement_type = models.CharField(max_length=30, choices=CashMovementType.choices, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Cash Movement'
        verbose_name_plural = 'Cash Movements'

    def __str__(self):
        return f"{self.movement_type} {self.amount} @ {self.created_at}"


class CashClosing(models.Model):
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    real_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    difference = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    closed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Cash Closing'
        verbose_name_plural = 'Cash Closings'

    def __str__(self):
        return f"Closing @ {self.closed_at} (expected={self.expected_amount} real={self.real_amount})"
