from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import CashOpening, CashMovement, CashClosing, CashStatus, CashMovementType


class CashError(Exception):
    pass


def get_current_opening():
    return CashOpening.objects.filter(status=CashStatus.OPEN).order_by('opened_at').last()


def ensure_opening():
    op = get_current_opening()
    if not op:
        raise CashError('No cash opening found. Open the cash before registering movements.')
    return op


def open_cash(opening_amount, opened_by=None):
    if get_current_opening():
        raise CashError('There is already an open cash.')
    return CashOpening.objects.create(opening_amount=Decimal(opening_amount or 0), opened_by=opened_by)


@transaction.atomic
def register_movement(movement_type, amount, reference='', notes='', created_by=None):
    op = ensure_opening()
    amount = Decimal(amount)
    if amount <= 0:
        raise CashError('Amount must be positive')
    mv = CashMovement.objects.create(movement_type=movement_type, amount=amount, reference=reference or '', notes=notes or '', created_by=created_by)
    return mv


@transaction.atomic
def register_sale_payment(sale, amount, user=None, ip=None, notes=''):
    # create sale payment record first (to update sale aggregates)
    # import here to avoid circular imports at module load
    from sales import services as sales_services
    payment = sales_services.register_payment(sale, amount, user=user, ip=ip, notes=notes)
    # register cash movement
    try:
        register_movement(CashMovementType.SALE_PAYMENT, amount, reference=f'sale:{sale.pk}', notes=notes, created_by=user)
    except Exception:
        # do not rollback sale payment if cash logging fails; caller can handle consistency
        pass
    return payment


def _movement_sign(mv_type):
    if mv_type in (CashMovementType.SALE_PAYMENT, CashMovementType.MANUAL_IN):
        return 1
    return -1


def get_expected_amount(opening: CashOpening):
    # sum movements since opening
    qs = CashMovement.objects.filter(created_at__gte=opening.opened_at)
    total = Decimal('0.00')
    for m in qs:
        total += Decimal(m.amount or 0) * _movement_sign(m.movement_type)
    return (Decimal(opening.opening_amount or 0) + total)


def get_movements_since_opening(opening: CashOpening):
    return CashMovement.objects.filter(created_at__gte=opening.opened_at).order_by('created_at')


def generate_closing_report(opening: CashOpening):
    movements = get_movements_since_opening(opening)
    totals_by_type = {}
    total_in = Decimal('0.00')
    total_out = Decimal('0.00')
    for m in movements:
        totals_by_type.setdefault(m.movement_type, Decimal('0.00'))
        totals_by_type[m.movement_type] += Decimal(m.amount or 0)
        if _movement_sign(m.movement_type) > 0:
            total_in += Decimal(m.amount or 0)
        else:
            total_out += Decimal(m.amount or 0)

    expected = (Decimal(opening.opening_amount or 0) + total_in - total_out)
    report = {
        'opening': opening,
        'movements': movements,
        'totals_by_type': totals_by_type,
        'total_in': total_in,
        'total_out': total_out,
        'expected': expected,
    }
    return report


@transaction.atomic
def close_cash(real_amount, closed_by=None):
    op = ensure_opening()
    expected = get_expected_amount(op)
    real = Decimal(real_amount)
    diff = real - expected
    closing = CashClosing.objects.create(expected_amount=expected, real_amount=real, difference=diff, closed_by=closed_by, closed_at=timezone.now())
    op.status = CashStatus.CLOSED
    op.save(update_fields=['status'])
    return closing


__all__ = ['CashError', 'get_current_opening', 'open_cash', 'register_movement', 'register_sale_payment', 'get_expected_amount', 'close_cash']
