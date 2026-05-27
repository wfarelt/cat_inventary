from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from products.models import Product
from purchases.models import Supplier, Purchase, PurchaseItem, PurchaseStatus
from purchases import services as purchase_services
from inventory.models import ProductCostHistory, StockMovement

User = get_user_model()


class PurchaseServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('purchaser', 'p@example.com', 'pass')
        self.supplier = Supplier.objects.create(name='ACME')
        self.product = Product.objects.create(code='PR1', description='Prod1', stock=5, cost=Decimal('10.00'))

    def _create_purchase_with_item(self, qty=1, cost='12.00'):
        p = Purchase.objects.create(supplier=self.supplier, created_by=self.user)
        PurchaseItem.objects.create(purchase=p, product=self.product, quantity=Decimal(qty), unit_cost=Decimal(cost))
        p.recalc_totals(); p.save()
        return p

    def test_confirm_purchase_increases_stock_and_updates_cost(self):
        p = self._create_purchase_with_item(qty=3, cost='12.00')
        purchase_services.confirm_purchase(p, user=self.user)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, Decimal('8'))
        self.assertEqual(self.product.cost, Decimal('12.00'))
        # check cost history and stock movement
        ch = ProductCostHistory.objects.filter(product=self.product).last()
        self.assertIsNotNone(ch)
        m = StockMovement.objects.filter(product=self.product, movement_type='PURCHASE').last()
        self.assertIsNotNone(m)

    def test_confirm_purchase_requires_items(self):
        p = Purchase.objects.create(supplier=self.supplier, created_by=self.user)
        with self.assertRaises(purchase_services.PurchaseError):
            purchase_services.confirm_purchase(p, user=self.user)

    def test_confirm_purchase_invalid_item_values(self):
        p = Purchase.objects.create(supplier=self.supplier, created_by=self.user)
        PurchaseItem.objects.create(purchase=p, product=self.product, quantity=Decimal('0'), unit_cost=Decimal('5.00'))
        with self.assertRaises(purchase_services.PurchaseError):
            purchase_services.confirm_purchase(p, user=self.user)
        # zero cost
        p2 = Purchase.objects.create(supplier=self.supplier, created_by=self.user)
        PurchaseItem.objects.create(purchase=p2, product=self.product, quantity=Decimal('1'), unit_cost=Decimal('0'))
        with self.assertRaises(purchase_services.PurchaseError):
            purchase_services.confirm_purchase(p2, user=self.user)

    def test_cancel_purchase_reverts_stock_and_status(self):
        p = self._create_purchase_with_item(qty=2, cost='15.00')
        purchase_services.confirm_purchase(p, user=self.user)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, Decimal('7'))
        # now cancel
        purchase_services.cancel_purchase(p, user=self.user)
        p.refresh_from_db()
        self.assertEqual(p.status, PurchaseStatus.CANCELLED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, Decimal('5'))

    def test_cancel_only_confirmed(self):
        p = self._create_purchase_with_item(qty=1, cost='9.00')
        with self.assertRaises(purchase_services.PurchaseError):
            purchase_services.cancel_purchase(p, user=self.user)
