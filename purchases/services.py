from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from inventory import services as inv_services
from inventory.models import MovementType, CostSource
from .models import Purchase, PurchaseItem, PurchaseStatus, PurchaseAudit


class PurchaseError(Exception):
    pass


def _ensure_draft(purchase: Purchase):
    if purchase.status != PurchaseStatus.DRAFT:
        raise PurchaseError('Only DRAFT purchases can be confirmed')


def _ensure_confirmed(purchase: Purchase):
    if purchase.status != PurchaseStatus.CONFIRMED:
        raise PurchaseError('Only CONFIRMED purchases can be cancelled')


@transaction.atomic
def confirm_purchase(purchase: Purchase, user=None, ip=None):
    """Confirm a purchase: increase stock, update cost, register movements, set status to CONFIRMED."""
    _ensure_draft(purchase)
    items = list(purchase.items.select_related('product').all())
    if not items:
        raise PurchaseError('Purchase must have at least one item')

    # Recalculate totals and persist
    purchase.recalc_totals()
    purchase.save(update_fields=['subtotal', 'total'])

    # Process items: increase stock and update last cost per item
    for it in items:
        if Decimal(it.quantity) <= 0:
            raise PurchaseError('Item quantity must be greater than zero')
        if Decimal(it.unit_cost) <= 0:
            raise PurchaseError('Item unit_cost must be greater than zero')

        # increase stock and register movement of type PURCHASE
        inv_services.increase_stock(
            product=it.product,
            quantity=it.quantity,
            user=user,
            movement_type=MovementType.PURCHASE,
            unit_cost=it.unit_cost,
            reason=f'Purchase #{purchase.pk}',
            reference=f'purchase:{purchase.pk}',
            source_cost=CostSource.PURCHASE,
        )

    purchase.status = PurchaseStatus.CONFIRMED
    purchase.save(update_fields=['status'])
    # Audit
    try:
        PurchaseAudit.objects.create(purchase=purchase, event='CONFIRMED', user=user, ip=ip, detail=f'Confirmed purchase #{purchase.pk}')
    except Exception:
        # Never fail the whole flow due to audit logging
        pass
    return purchase


@transaction.atomic
def cancel_purchase(purchase: Purchase, user=None, ip=None):
    """Cancel a confirmed purchase: revert stock, register manual correction movements, set status CANCELLED."""
    _ensure_confirmed(purchase)
    items = list(purchase.items.select_related('product').all())

    # Revert inventory
    for it in items:
        # decrease stock: this will enforce available_stock rules via inventory.services
        inv_services.decrease_stock(
            product=it.product,
            quantity=it.quantity,
            user=user,
            movement_type=MovementType.MANUAL_CORRECTION,
            unit_cost=None,
            reason=f'Cancel Purchase #{purchase.pk}',
            reference=f'purchase:{purchase.pk}',
        )

    purchase.status = PurchaseStatus.CANCELLED
    purchase.save(update_fields=['status'])
    # Audit
    try:
        PurchaseAudit.objects.create(purchase=purchase, event='CANCELLED', user=user, ip=ip, detail=f'Cancelled purchase #{purchase.pk}')
    except Exception:
        pass
    return purchase


__all__ = ['confirm_purchase', 'cancel_purchase', 'PurchaseError']
