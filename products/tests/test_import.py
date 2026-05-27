from io import BytesIO
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from openpyxl import Workbook
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from products.models import Product


@override_settings(MIDDLEWARE=[
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])
class ImportTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'pass')
        self.client = Client()
        self.client.login(username='admin', password='pass')

    def make_workbook(self):
        wb = Workbook()
        ws = wb.active
        headers = ['code', 'category', 'description', 'cost', 'price', 'stock', 'stock_min', 'ruc']
        ws.append(headers)
        ws.append(['ABC123', 'Engine', 'Filter ABC', '10.5', '20.0', '5', '1', '12345678901'])
        ws.append(['', 'Engine', 'Missing code', '5', '10', '2', '0', '12345678901'])
        ws.append(['XYZ!@#', 'Misc', 'Bad code chars', '1', '-5', '1', '0', '123'])
        bio = BytesIO()
        wb.save(bio)
        bio.seek(0)
        return bio

    def test_import_preview_and_errors(self):
        wb = self.make_workbook()
        upload = SimpleUploadedFile('test.xlsx', wb.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp = self.client.post(reverse('product_import'), {'file': upload})
        self.assertEqual(resp.status_code, 200)
        sess = self.client.session
        self.assertIn('import_rows', sess)
        rows = sess['import_rows']
        # rows: three data rows
        self.assertEqual(len(rows), 3)
        # second row had missing code -> error
        missing = next(r for r in rows if r.get('_row_number') == 3)
        self.assertIn('code', missing.get('errors', {}))
        # third row had invalid code chars and negative price and invalid ruc
        bad = next(r for r in rows if r.get('_row_number') == 4)
        self.assertIn('price', bad.get('errors', {}))
        self.assertIn('code', bad.get('errors', {}))
        self.assertIn('ruc', bad.get('errors', {}))

    def test_confirm_respects_selection_and_skips_errors(self):
        # prepare session rows: one valid, one invalid
        valid = {'_row_number': 2, 'code': 'SEL1', 'description': 'Sel one', 'category': 'Engine', 'cost': '1', 'price': '10', 'stock': '2', 'stock_min': '0', 'errors': {}}
        invalid = {'_row_number': 3, 'code': 'SEL2', 'description': 'Bad', 'category': 'Engine', 'cost': '1', 'price': '-5', 'stock': '1', 'stock_min': '0', 'errors': {'price': ['Valor negativo']}}
        sess = self.client.session
        sess['import_rows'] = [valid, invalid]
        sess.save()

        resp = self.client.post(reverse('product_import_confirm'), {'action': 'add_new', 'selected_rows': ['2']})
        # product SEL1 should be created, SEL2 skipped
        self.assertTrue(Product.objects.filter(code='SEL1').exists())
        self.assertFalse(Product.objects.filter(code='SEL2').exists())
