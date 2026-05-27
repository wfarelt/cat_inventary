from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import StockMovement, MovementType, ProductCostHistory, CostSource


class InventoryError(Exception):
    pass


def _to_decimal(value):
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(value)
    except Exception:
        raise InventoryError('Invalid quantity')


def _get_product(product):
    # accept instance or pk
    from products.models import Product
    if isinstance(product, Product):
        return product
    return Product.objects.get(pk=product)


def register_movement(product, movement_type, quantity, previous_stock, new_stock, user=None, unit_cost=None, reason='', reference=None, notes=''):
    return StockMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        unit_cost=unit_cost,
        reason=reason or '',
        reference=reference,
        notes=notes or '',
        created_by=user,
        created_at=timezone.now(),
    )


def update_last_cost(product, new_cost, user=None, source=CostSource.MANUAL):
    new_cost = Decimal(new_cost)
    previous = product.cost
    if previous is None or Decimal(previous) != new_cost:
        # save history and update product
        ProductCostHistory.objects.create(
            product=product,
            previous_cost=previous,
            new_cost=new_cost,
            source=source,
            created_by=user,
        )
        product.cost = new_cost
        product.save(update_fields=['cost'])


@transaction.atomic
def increase_stock(product, quantity, user=None, movement_type=MovementType.PURCHASE, unit_cost=None, reason='Adjustment', reference=None, source_cost=CostSource.MANUAL):
    product = _get_product(product)
    q = _to_decimal(quantity)
    if q <= 0:
        raise InventoryError('Quantity must be positive')
    prev = Decimal(product.stock or 0)
    new = prev + q
    # update cost if provided
    if unit_cost is not None:
        update_last_cost(product, unit_cost, user=user, source=source_cost)
    product.stock = new
    product.save(update_fields=['stock'])
    return register_movement(product=product, movement_type=movement_type, quantity=q, previous_stock=prev, new_stock=new, user=user, unit_cost=unit_cost, reason=reason, reference=reference)


@transaction.atomic
def decrease_stock(product, quantity, user=None, movement_type=MovementType.ADJUSTMENT_OUT, unit_cost=None, reason='Adjustment', reference=None):
    product = _get_product(product)
    q = _to_decimal(quantity)
    if q <= 0:
        raise InventoryError('Quantity must be positive')
    available = Decimal(product.available_stock or 0)
    if available - q < 0:
        raise InventoryError('Stock insuficiente')
    prev = Decimal(product.stock or 0)
    new = prev - q
    product.stock = new
    product.save(update_fields=['stock'])
    return register_movement(product=product, movement_type=movement_type, quantity=q, previous_stock=prev, new_stock=new, user=user, unit_cost=unit_cost, reason=reason, reference=reference)


@transaction.atomic
def reserve_stock(product, quantity, user=None, reason='Reserve'):
    product = _get_product(product)
    q = _to_decimal(quantity)
    if q <= 0:
        raise InventoryError('Quantity must be positive')
    available = Decimal(product.available_stock or 0)
    if available - q < 0:
        raise InventoryError('Stock insuficiente')
    prev_reserved = Decimal(product.stock_reserved or 0)
    new_reserved = prev_reserved + q
    product.stock_reserved = new_reserved
    product.save(update_fields=['stock_reserved'])
    # audit as manual correction
    return register_movement(product=product, movement_type=MovementType.MANUAL_CORRECTION, quantity=q, previous_stock=Decimal(product.stock or 0), new_stock=Decimal(product.stock or 0), user=user, unit_cost=None, reason=reason)


@transaction.atomic
def release_stock(product, quantity, user=None, reason='Release'):
    product = _get_product(product)
    q = _to_decimal(quantity)
    if q <= 0:
        raise InventoryError('Quantity must be positive')
    prev_reserved = Decimal(product.stock_reserved or 0)
    if prev_reserved - q < 0:
        raise InventoryError('Releasing more than reserved')
    new_reserved = prev_reserved - q
    product.stock_reserved = new_reserved
    product.save(update_fields=['stock_reserved'])
    return register_movement(product=product, movement_type=MovementType.MANUAL_CORRECTION, quantity=q, previous_stock=Decimal(product.stock or 0), new_stock=Decimal(product.stock or 0), user=user, unit_cost=None, reason=reason)


@transaction.atomic
def adjust_stock(product, quantity, in_or_out, user=None, reason=None, reference=None):
    if in_or_out not in ('in', 'out'):
        raise InventoryError('in_or_out must be "in" or "out"')
    if not reason:
        raise InventoryError('Reason obligatorio')
    if in_or_out == 'in':
        return increase_stock(product, quantity, user=user, movement_type=MovementType.ADJUSTMENT_IN, reason=reason, reference=reference)
    else:
        return decrease_stock(product, quantity, user=user, movement_type=MovementType.ADJUSTMENT_OUT, reason=reason, reference=reference)


@transaction.atomic
def register_return(product, quantity, return_type, user=None, reason=None, reference=None):
    if return_type not in (MovementType.CUSTOMER_RETURN, MovementType.SUPPLIER_RETURN):
        raise InventoryError('Invalid return type')
    if not reason:
        raise InventoryError('Reason obligatorio')
    if return_type == MovementType.CUSTOMER_RETURN:
        # customer return increases stock
        return increase_stock(product, quantity, user=user, movement_type=MovementType.CUSTOMER_RETURN, reason=reason, reference=reference)
    else:
        # supplier return decreases stock
        return decrease_stock(product, quantity, user=user, movement_type=MovementType.SUPPLIER_RETURN, reason=reason, reference=reference)


__all__ = [
    'InventoryError', 'increase_stock', 'decrease_stock', 'reserve_stock', 'release_stock', 'adjust_stock', 'register_return', 'update_last_cost', 'register_movement'
]
