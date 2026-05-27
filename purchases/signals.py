from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchase, PurchaseAudit


@receiver(post_save, sender=Purchase)
def purchase_post_save(sender, instance: Purchase, created, **kwargs):
    """Log audit entries for creation and edits. Uses Purchase.created_by when available."""
    try:
        if created:
            PurchaseAudit.objects.create(purchase=instance, event='CREATED', user=getattr(instance, 'created_by', None), detail=f'Purchase #{instance.pk} created')
        else:
            PurchaseAudit.objects.create(purchase=instance, event='EDITED', user=getattr(instance, 'created_by', None), detail=f'Purchase #{instance.pk} updated')
    except Exception:
        # avoid breaking saves if audit fails
        pass
