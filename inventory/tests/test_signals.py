from decimal import Decimal
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from products.models import Product
from inventory.models import ProductCostHistory, ProductPriceHistory

User = get_user_model()


class SignalsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('sigtester', 's@example.com', 'pass')

    def test_cost_history_created_on_update(self):
        p = Product.objects.create(code='PX', description='SigProduct', cost=Decimal('5.00'))
        # update cost
        p.cost = Decimal('7.00')
        p.save()
        ph = ProductCostHistory.objects.filter(product=p).last()
        self.assertIsNotNone(ph)
        self.assertEqual(ph.previous_cost, Decimal('5.00'))
        self.assertEqual(ph.new_cost, Decimal('7.00'))

    def test_price_history_created_on_update(self):
        p = Product.objects.create(code='PY', description='SigProduct2', price=Decimal('100.00'))
        p.price = Decimal('110.00')
        p.save()
        ph = ProductPriceHistory.objects.filter(product=p).last()
        self.assertIsNotNone(ph)
        self.assertEqual(ph.previous_price, Decimal('100.00'))
        self.assertEqual(ph.new_price, Decimal('110.00'))
