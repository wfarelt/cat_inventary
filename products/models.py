from django.db import models
from core.models import TimeStampedModel
from django.urls import reverse


class Category(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    code = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.CharField(max_length=255, db_index=True)
    cross_reference = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    brand = models.CharField(max_length=100, default='CATERPILLAR', db_index=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_reserved = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_min = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='products/%Y/%m', blank=True, null=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['description']),
        ]

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)

    @property
    def available_stock(self):
        return (self.stock or 0) - (self.stock_reserved or 0)

    def __str__(self):
        return f"{self.code} - {self.description}"

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])


class ProductKit(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Kit de Producto'
        verbose_name_plural = 'Kits de Producto'

    def __str__(self):
        return self.name


class ProductKitItem(models.Model):
    kit = models.ForeignKey(ProductKit, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    class Meta:
        unique_together = ('kit', 'product')

    def __str__(self):
        return f"{self.kit.name} - {self.product.code} x {self.quantity}"
