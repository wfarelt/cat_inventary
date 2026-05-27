from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from ..models import Product, Category


@override_settings(MIDDLEWARE=[
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])
class BulkInlineApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user('tester2', 't2@example.com', 'pass')
        # grant necessary perms
        perms = ['change_product', 'add_product', 'view_product']
        for codename in perms:
            p = Permission.objects.filter(codename=codename).first()
            if p:
                self.user.user_permissions.add(p)
        self.client.force_login(self.user)

    def test_bulk_set_price_uses_persisted_selection(self):
        p1 = Product.objects.create(code='B1', description='Bulk1', price=Decimal('10'), stock=5)
        p2 = Product.objects.create(code='B2', description='Bulk2', price=Decimal('20'), stock=2)
        # persist selection in session
        sess = self.client.session
        sess['bulk_selected'] = [p1.pk, p2.pk]
        sess.save()

        resp = self.client.post(reverse('product_bulk_action'), {'action': 'set_price', 'price_value': '50'})
        self.assertEqual(resp.status_code, 302)
        p1.refresh_from_db()
        p2.refresh_from_db()
        self.assertEqual(p1.price, Decimal('50'))
        self.assertEqual(p2.price, Decimal('50'))

    def test_inline_edit_updates_session_row(self):
        # prepare session import row
        sess = self.client.session
        sess['import_rows'] = [{'_row_number': 2, 'code': 'INL1', 'description': 'X', 'category': 'C', 'cost': '1', 'price': '10', 'stock': '1', 'errors': {}}]
        sess.save()

        resp = self.client.post(reverse('product_import_edit_cell'), {'row': '2', 'header': 'price', 'value': '15.5'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        sess = self.client.session
        rows = sess.get('import_rows', [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['price'], '15.5')

    def test_api_product_list_filters_and_ordering(self):
        cat_a = Category.objects.create(name='A')
        cat_b = Category.objects.create(name='B')
        Product.objects.create(code='P1', description='One', category=cat_a, price=Decimal('10'), stock=5)
        Product.objects.create(code='P2', description='Two', category=cat_b, price=Decimal('20'), stock=2)
        Product.objects.create(code='P3', description='Three', category=cat_a, price=Decimal('30'), stock=8)

        url = reverse('api_product_list')
        # filter by price range
        resp = self.client.get(url, {'price_min': '15', 'price_max': '35', 'ordering': '-price'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 2)
        codes = [r['code'] for r in data['results']]
        # ordered desc by price: P3 then P2
        self.assertEqual(codes, ['P3', 'P2'])
