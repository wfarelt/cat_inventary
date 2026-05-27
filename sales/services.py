from decimal import Decimal
from django.db import transaction

from inventory import services as inv_services
from inventory.models import MovementType

from .models import Sale, SaleItem, SaleStatus, SaleAudit, SalePayment


class SaleError(Exception):
    pass


def _get_items(sale: Sale):
    return list(sale.items.select_related('product').all())


@transaction.atomic
def reserve_sale(sale: Sale, user=None, ip=None, expiration_date=None):
    if sale.status not in (SaleStatus.PROFORMA, SaleStatus.PEDIDO):
        raise SaleError('Only PROFORMA or PEDIDO can be reserved')
    items = _get_items(sale)
    if not items:
        raise SaleError('Sale must have items to reserve')

    # attempt to reserve each product
    for it in items:
        inv_services.reserve_stock(it.product, it.quantity, user=user, reason=f'Reserve Sale #{sale.number or sale.pk}')

    sale.status = SaleStatus.RESERVA
    if expiration_date:
        sale.expiration_date = expiration_date
    sale.save(update_fields=['status', 'expiration_date'] if expiration_date else ['status'])
    try:
        SaleAudit.objects.create(sale=sale, event='RESERVED', user=user, ip=ip, detail=f'Reserved sale #{sale.number or sale.pk}')
    except Exception:
        pass
    return sale


@transaction.atomic
def release_reservation(sale: Sale, user=None, ip=None, reason='Reservation expired'):
    if sale.status != SaleStatus.RESERVA:
        raise SaleError('Only RESERVA sales can be released')
    items = _get_items(sale)
    for it in items:
        inv_services.release_stock(it.product, it.quantity, user=user, reason=reason)

    sale.status = SaleStatus.ANULADO
    sale.save(update_fields=['status'])
    try:
        SaleAudit.objects.create(sale=sale, event='RELEASED', user=user, ip=ip, detail=f'Reservation released for sale #{sale.number or sale.pk}: {reason}')
    except Exception:
        pass
    return sale


@transaction.atomic
def execute_sale(sale: Sale, user=None, ip=None):
    if sale.status not in (SaleStatus.PROFORMA, SaleStatus.PEDIDO, SaleStatus.RESERVA):
        raise SaleError('Sale cannot be executed from current status')
    items = _get_items(sale)
    if not items:
        raise SaleError('Sale must have items to execute')

    # Process items
    for it in items:
        # If reserved, release reserved and then decrease stock
        if sale.status == SaleStatus.RESERVA:
            # release reserved first (will validate reserved quantity)
            inv_services.release_stock(it.product, it.quantity, user=user, reason=f'Executing sale #{sale.number or sale.pk}')
            # then decrease physical stock
            inv_services.decrease_stock(it.product, it.quantity, user=user, movement_type=MovementType.SALE, reason=f'Execute Sale #{sale.number or sale.pk}', reference=f'sale:{sale.pk}')
        else:
            # validate and decrease available stock
            inv_services.decrease_stock(it.product, it.quantity, user=user, movement_type=MovementType.SALE, reason=f'Execute Sale #{sale.number or sale.pk}', reference=f'sale:{sale.pk}')

    sale.status = SaleStatus.EJECUTADO
    sale.save(update_fields=['status'])
    try:
        SaleAudit.objects.create(sale=sale, event='EXECUTED', user=user, ip=ip, detail=f'Executed sale #{sale.number or sale.pk}')
    except Exception:
        pass
    return sale


@transaction.atomic
def cancel_sale(sale: Sale, user=None, ip=None, reason='Sale cancelled'):
    # If reservation: release reserved
    if sale.status == SaleStatus.RESERVA:
        items = _get_items(sale)
        for it in items:
            inv_services.release_stock(it.product, it.quantity, user=user, reason=f'Cancel reservation #{sale.number or sale.pk}')
    elif sale.status == SaleStatus.EJECUTADO:
        items = _get_items(sale)
        for it in items:
            # customer return: increase stock back
            inv_services.register_return(it.product, it.quantity, MovementType.CUSTOMER_RETURN, user=user, reason=f'Cancel executed sale #{sale.number or sale.pk}', reference=f'sale:{sale.pk}')

    sale.status = SaleStatus.ANULADO
    sale.save(update_fields=['status'])
    try:
        SaleAudit.objects.create(sale=sale, event='CANCELLED', user=user, ip=ip, detail=f'Cancelled sale #{sale.number or sale.pk}: {reason}')
    except Exception:
        pass
    return sale


@transaction.atomic
def register_payment(sale: Sale, amount, user=None, ip=None, notes=''):
    amount = Decimal(amount)
    if amount <= 0:
        raise SaleError('Payment amount must be positive')
    payment = SalePayment.objects.create(sale=sale, amount=amount, created_by=user, notes=notes)
    try:
        SaleAudit.objects.create(sale=sale, event='PAYMENT', user=user, ip=ip, detail=f'Payment of {amount} for sale #{sale.number or sale.pk}')
    except Exception:
        pass
    return payment


__all__ = ['SaleError', 'reserve_sale', 'release_reservation', 'execute_sale', 'cancel_sale', 'register_payment']
