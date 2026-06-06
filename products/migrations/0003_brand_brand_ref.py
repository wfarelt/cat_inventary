from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    Brand = apps.get_model('products', 'Brand')
    Product = apps.get_model('products', 'Product')

    brand_names = (
        Product.objects.exclude(brand__isnull=True)
        .exclude(brand='')
        .values_list('brand', flat=True)
        .distinct()
    )

    brand_map = {}
    for name in brand_names:
        brand_obj, _ = Brand.objects.get_or_create(name=name)
        brand_map[name] = brand_obj.pk

    for product in Product.objects.all().iterator():
        brand_name = (product.brand or '').strip()
        if not brand_name:
            continue
        brand_pk = brand_map.get(brand_name)
        if brand_pk:
            product.brand_ref_id = brand_pk
            product.save(update_fields=['brand_ref'])


def backwards(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Product.objects.update(brand_ref=None)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_category_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'verbose_name': 'Marca',
                'verbose_name_plural': 'Marcas',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='brand_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.brand'),
        ),
        migrations.RunPython(forwards, backwards),
    ]
