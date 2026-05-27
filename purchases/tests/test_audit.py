from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from purchases.models import Supplier, Purchase, PurchaseItem, PurchaseAudit
from purchases import services as purchase_services
from products.models import Product

User = get_user_model()


class PurchaseAuditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('auditor', 'a@example.com', 'pass')
        self.supplier = Supplier.objects.create(name='ACME')
        self.product = Product.objects.create(code='PRX', description='ProdX', stock=2, cost=Decimal('5.00'))

    def _create_purchase(self):
        p = Purchase.objects.create(supplier=self.supplier, created_by=self.user)
        PurchaseItem.objects.create(purchase=p, product=self.product, quantity=Decimal('1'), unit_cost=Decimal('6.00'))
        p.recalc_totals(); p.save()
        return p

    def test_purchase_create_generates_audit(self):
        p = self._create_purchase()
        audits = PurchaseAudit.objects.filter(purchase=p)
        self.assertTrue(audits.filter(event='CREATED').exists())

    def test_confirm_generates_audit_with_user(self):
        p = self._create_purchase()
        purchase_services.confirm_purchase(p, user=self.user)
        self.assertTrue(PurchaseAudit.objects.filter(purchase=p, event='CONFIRMED', user=self.user).exists())

    def test_cancel_generates_audit_with_user(self):
        p = self._create_purchase()
        purchase_services.confirm_purchase(p, user=self.user)
        purchase_services.cancel_purchase(p, user=self.user)
        self.assertTrue(PurchaseAudit.objects.filter(purchase=p, event='CANCELLED', user=self.user).exists())
