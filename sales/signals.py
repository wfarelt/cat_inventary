from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Sale, SalePayment, SaleAudit


@receiver(post_save, sender=Sale)
def sale_post_save(sender, instance: Sale, created, **kwargs):
    try:
        if created:
            SaleAudit.objects.create(sale=instance, event='CREATED', user=getattr(instance, 'created_by', None), detail=f'Sale #{instance.number or instance.pk} created')
        else:
            SaleAudit.objects.create(sale=instance, event='EDITED', user=getattr(instance, 'created_by', None), detail=f'Sale #{instance.number or instance.pk} updated')
    except Exception:
        pass


@receiver(post_save, sender=SalePayment)
def salepayment_post_save(sender, instance: SalePayment, created, **kwargs):
    if not created:
        return
    try:
        SaleAudit.objects.create(sale=instance.sale, event='PAYMENT', user=getattr(instance, 'created_by', None), detail=f'Payment of {instance.amount} registered')
    except Exception:
        pass
