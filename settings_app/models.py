from django.db import models
from core.models import TimeStampedModel


class SiteConfiguration(TimeStampedModel):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'

    def __str__(self):
        return self.key
