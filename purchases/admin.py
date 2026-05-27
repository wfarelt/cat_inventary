from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html

from .models import Supplier, Purchase, PurchaseItem, PurchaseStatus
from .forms import PurchaseForm, PurchaseItemForm
from . import services as purchase_services


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    form = PurchaseItemForm
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    inlines = [PurchaseItemInline]
    list_display = ('id', 'supplier', 'purchase_date', 'invoice_number', 'subtotal', 'discount', 'total', 'status', 'created_by')
    search_fields = ('supplier__name', 'invoice_number')
    list_filter = ('status', 'purchase_date')
    readonly_fields = ('subtotal', 'total')
    actions = ['action_confirm', 'action_cancel']

    def action_confirm(self, request, queryset):
        success = 0
        errors = []
        for purchase in queryset:
            try:
                with transaction.atomic():
                    purchase_services.confirm_purchase(purchase, user=request.user)
                success += 1
            except Exception as e:
                errors.append(f"{purchase.pk}: {e}")
        if success:
            self.message_user(request, f"{success} purchases confirmed", level=messages.SUCCESS)
        if errors:
            for e in errors:
                self.message_user(request, e, level=messages.ERROR)
    action_confirm.short_description = 'Confirm selected purchases'

    def action_cancel(self, request, queryset):
        success = 0
        errors = []
        for purchase in queryset:
            try:
                with transaction.atomic():
                    purchase_services.cancel_purchase(purchase, user=request.user)
                success += 1
            except Exception as e:
                errors.append(f"{purchase.pk}: {e}")
        if success:
            self.message_user(request, f"{success} purchases cancelled", level=messages.SUCCESS)
        if errors:
            for e in errors:
                self.message_user(request, e, level=messages.ERROR)
    action_cancel.short_description = 'Cancel selected purchases'
