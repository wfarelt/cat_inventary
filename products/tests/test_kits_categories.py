from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Permission
from users.models import User
from ..models import Brand, Category, Product, ProductKit, ProductKitItem


class KitsCategoriesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('tester', 't@example.com', 'pass')
        perms = ['add_category', 'change_category', 'delete_category', 'view_category', 'add_brand', 'change_brand', 'delete_brand', 'view_brand', 'add_product', 'change_product', 'add_productkit', 'change_productkit']
        for codename in perms:
            p = Permission.objects.filter(codename=codename).first()
            if p:
                self.user.user_permissions.add(p)
        self.client.force_login(self.user)

    def test_category_crud(self):
        # create
        resp = self.client.post(reverse('category_create'), {'name': 'TestCat', 'description': 'x', 'is_active': True})
        self.assertEqual(resp.status_code, 302)
        cat = Category.objects.get(name='TestCat')
        # edit
        resp = self.client.post(reverse('category_edit', args=[cat.pk]), {'name': 'TestCat2', 'description': 'y', 'is_active': True})
        self.assertEqual(resp.status_code, 302)
        cat.refresh_from_db()
        self.assertEqual(cat.name, 'TestCat2')
        # delete (no products)
        resp = self.client.post(reverse('category_delete', args=[cat.pk]), {})
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Category.objects.filter(pk=cat.pk).exists())

    def test_brand_crud(self):
        resp = self.client.post(reverse('brand_create'), {'name': 'BrandX', 'description': 'x', 'is_active': True})
        self.assertEqual(resp.status_code, 302)
        brand = Brand.objects.get(name='BrandX')

        resp = self.client.post(reverse('brand_edit', args=[brand.pk]), {'name': 'BrandY', 'description': 'y', 'is_active': True})
        self.assertEqual(resp.status_code, 302)
        brand.refresh_from_db()
        self.assertEqual(brand.name, 'BrandY')

        resp = self.client.post(reverse('brand_delete', args=[brand.pk]), {})
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Brand.objects.filter(pk=brand.pk).exists())

    def test_kit_create_and_add_item(self):
        # create product
        prod = Product.objects.create(code='P1', description='Prod1')
        # create kit
        resp = self.client.post(reverse('kit_create'), {'name': 'K1', 'description': 'kit', 'is_active': True})
        self.assertEqual(resp.status_code, 302)
        kit = ProductKit.objects.get(name='K1')
        # add item
        resp = self.client.post(reverse('kit_add_item', args=[kit.pk]), {'product': prod.pk, 'quantity': '2'})
        self.assertEqual(resp.status_code, 302)
        items = ProductKitItem.objects.filter(kit=kit)
        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first().quantity, 2)
