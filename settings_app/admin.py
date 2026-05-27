from django.contrib import admin
from .models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key',)
