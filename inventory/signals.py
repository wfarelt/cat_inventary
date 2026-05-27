from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings

from products.models import Product
from .models import ProductCostHistory, ProductPriceHistory, CostSource


ENABLED = getattr(settings, 'INVENTORY_AUTO_HISTORY', True)


@receiver(pre_save, sender=Product)
def _store_old_cost_price(sender, instance, **kwargs):
    if not ENABLED:
        return
    if not instance.pk:
        instance._old_cost = None
        instance._old_price = None
        return
    try:
        old = sender.objects.get(pk=instance.pk)
        instance._old_cost = old.cost
        instance._old_price = old.price
    except sender.DoesNotExist:
        instance._old_cost = None
        instance._old_price = None


@receiver(post_save, sender=Product)
def _create_cost_price_history(sender, instance, created, **kwargs):
    if not ENABLED:
        return
    # handle cost change
    old_cost = getattr(instance, '_old_cost', None)
    new_cost = instance.cost
    if old_cost is None and created and new_cost is not None:
        # initial cost set on create
        ProductCostHistory.objects.create(product=instance, previous_cost=None, new_cost=new_cost, source=CostSource.MANUAL)
    elif old_cost is not None and new_cost is not None and old_cost != new_cost:
        ProductCostHistory.objects.create(product=instance, previous_cost=old_cost, new_cost=new_cost, source=CostSource.MANUAL)

    # handle price change
    old_price = getattr(instance, '_old_price', None)
    new_price = instance.price
    if old_price is None and created and new_price is not None:
        ProductPriceHistory.objects.create(product=instance, previous_price=None, new_price=new_price)
    elif old_price is not None and new_price is not None and old_price != new_price:
        ProductPriceHistory.objects.create(product=instance, previous_price=old_price, new_price=new_price)
