from django.contrib import admin
from .models import CashOpening, CashMovement, CashClosing


@admin.register(CashOpening)
class CashOpeningAdmin(admin.ModelAdmin):
    list_display = ('opened_at', 'opening_amount', 'opened_by', 'status')
    list_filter = ('status',)
    search_fields = ('opened_by__username',)


@admin.register(CashMovement)
class CashMovementAdmin(admin.ModelAdmin):
    list_display = ('movement_type', 'amount', 'reference', 'created_at', 'created_by')
    list_filter = ('movement_type',)
    search_fields = ('reference',)


@admin.register(CashClosing)
class CashClosingAdmin(admin.ModelAdmin):
    list_display = ('closed_at', 'expected_amount', 'real_amount', 'difference', 'closed_by')
    search_fields = ('closed_by__username',)
