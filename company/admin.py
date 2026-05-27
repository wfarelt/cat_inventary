from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ruc', 'phone', 'email', 'is_active')
    search_fields = ('name', 'ruc')
