from django.contrib import admin
from .models import Sale, SaleItem, SalePayment, SaleAudit, Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'is_active', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('is_active',)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'status', 'sale_date', 'total', 'paid_amount', 'pending_amount')
    search_fields = ('number', 'customer__name')
    list_filter = ('status', 'sale_date')
    inlines = (SaleItemInline,)


@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):
    list_display = ('sale', 'amount', 'payment_date', 'created_by')
    search_fields = ('sale__number',)


@admin.register(SaleAudit)
class SaleAuditAdmin(admin.ModelAdmin):
    list_display = ('sale', 'event', 'user', 'created_at')
    search_fields = ('sale__number', 'event', 'detail')
