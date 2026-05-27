from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_SALES = 'sales'
    ROLE_ACCOUNTING = 'accounting'
    ROLE_WAREHOUSE = 'warehouse'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_SALES, 'Sales'),
        (ROLE_ACCOUNTING, 'Accounting'),
        (ROLE_WAREHOUSE, 'Warehouse'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SALES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
