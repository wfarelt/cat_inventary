from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator

from django.forms import inlineformset_factory

from .models import Purchase, PurchaseItem, PurchaseStatus
from .forms import PurchaseForm, PurchaseItemForm
from . import services as purchase_services


def purchase_list(request):
    qs = Purchase.objects.select_related('supplier', 'created_by').order_by('-purchase_date')
    status = request.GET.get('status')
    supplier = request.GET.get('supplier')
    if status:
        qs = qs.filter(status=status)
    if supplier:
        qs = qs.filter(supplier_id=supplier)
    paginator = Paginator(qs, 25)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'purchases/list.html', {'page_obj': page_obj})


def purchase_create(request):
    ItemFormSet = inlineformset_factory(Purchase, PurchaseItem, form=PurchaseItemForm, extra=1, can_delete=True)
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            purchase.save()
            formset = ItemFormSet(request.POST, instance=purchase)
            if formset.is_valid():
                formset.save()
                purchase.recalc_totals()
                purchase.save(update_fields=['subtotal', 'total'])
                messages.success(request, 'Purchase created (DRAFT)')
                return redirect(reverse('purchases:purchase_detail', args=[purchase.pk]))
            else:
                purchase.delete()
        else:
            formset = ItemFormSet(request.POST)
    else:
        form = PurchaseForm()
        formset = ItemFormSet()
    return render(request, 'purchases/form.html', {'form': form, 'formset': formset})


def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase.objects.prefetch_related('items__product').select_related('supplier', 'created_by'), pk=pk)
    return render(request, 'purchases/detail.html', {'purchase': purchase})


def purchase_confirm(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    try:
        with transaction.atomic():
            purchase_services.confirm_purchase(purchase, user=request.user)
        messages.success(request, 'Purchase confirmed')
    except Exception as e:
        messages.error(request, f'Error confirming purchase: {e}')
    return redirect(reverse('purchases:purchase_detail', args=[pk]))


def purchase_cancel(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    try:
        with transaction.atomic():
            purchase_services.cancel_purchase(purchase, user=request.user)
        messages.success(request, 'Purchase cancelled')
    except Exception as e:
        messages.error(request, f'Error cancelling purchase: {e}')
    return redirect(reverse('purchases:purchase_detail', args=[pk]))
