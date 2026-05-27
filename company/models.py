from django.db import models
from core.models import TimeStampedModel


class Company(TimeStampedModel):
    name = models.CharField(max_length=200, db_index=True)
    ruc = models.CharField(max_length=32, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.name
