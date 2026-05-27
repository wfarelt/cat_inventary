from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from products.models import Product
from inventory import services
from inventory.models import StockMovement, ProductCostHistory


User = get_user_model()


class InventoryServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 't@example.com', 'pass')
        self.product = Product.objects.create(code='P1', description='Test product', stock=10, stock_reserved=0, cost=Decimal('10.00'))

    def test_increase_and_decrease_stock_and_movements(self):
        services.increase_stock(self.product, 5, user=self.user, unit_cost=Decimal('12.00'), reason='Entrada prueba')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, Decimal('15'))
        # movement created
        m = StockMovement.objects.filter(product=self.product).last()
        self.assertIsNotNone(m)
        self.assertEqual(m.quantity, Decimal('5'))

        services.decrease_stock(self.product, 3, user=self.user, reason='Salida prueba')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, Decimal('12'))

    def test_decrease_stock_insufficient_raises(self):
        # try to decrease more than available
        with self.assertRaises(services.InventoryError):
            services.decrease_stock(self.product, 20, user=self.user, reason='Test')

    def test_reserve_and_release(self):
        services.reserve_stock(self.product, 4, user=self.user, reason='Reservar')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_reserved, Decimal('4'))
        services.release_stock(self.product, 2, user=self.user, reason='Liberar')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_reserved, Decimal('2'))
        with self.assertRaises(services.InventoryError):
            services.release_stock(self.product, 10, user=self.user, reason='Liberar mas')

    def test_adjust_stock_in_out(self):
        services.adjust_stock(self.product, 2, 'in', user=self.user, reason='Ajuste in')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, Decimal('12'))
        services.adjust_stock(self.product, 2, 'out', user=self.user, reason='Ajuste out')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, Decimal('10'))

    def test_register_return_customer_and_supplier(self):
        services.register_return(self.product, 1, services.MovementType.CUSTOMER_RETURN, user=self.user, reason='Devolucion cliente')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, Decimal('11'))
        # supplier return should decrease
        with self.assertRaises(services.InventoryError):
            # try big supplier return that would make available negative
            services.register_return(self.product, 100, services.MovementType.SUPPLIER_RETURN, user=self.user, reason='Devolucion proveedor')

    def test_update_last_cost_creates_history(self):
        services.update_last_cost(self.product, Decimal('15.50'), user=self.user, source=services.CostSource.MANUAL)
        self.product.refresh_from_db()
        self.assertEqual(self.product.cost, Decimal('15.50'))
        ph = ProductCostHistory.objects.filter(product=self.product).last()
        self.assertIsNotNone(ph)
        self.assertEqual(ph.previous_cost, Decimal('10.00'))
        self.assertEqual(ph.new_cost, Decimal('15.50'))
