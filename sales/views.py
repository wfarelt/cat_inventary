from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.db import transaction

from .forms import SaleForm, SaleItemFormSet, QuickCustomerForm
from .models import Sale, Customer, SaleStatus
from . import services as sales_services
from cash import services as cash_services
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import render_to_string
from . import utils_pdf


def _get_default_customer():
    c, _ = Customer.objects.get_or_create(name='Walk-in')
    return c


def fast_sale(request):
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)
        quick_customer = QuickCustomerForm(request.POST)

        if sale_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # resolve customer: prefer sale form selection, else quick customer, else default
                    customer = sale_form.cleaned_data.get('customer')
                    if not customer:
                        if quick_customer.is_valid() and quick_customer.cleaned_data.get('name'):
                            customer = quick_customer.save()
                        else:
                            customer = _get_default_customer()

                    sale = sale_form.save(commit=False)
                    sale.customer = customer
                    sale.recalc_totals()
                    sale.save()
                    formset.instance = sale
                    formset.save()

                    # If sale created with status EJECUTADO, attempt to execute immediately
                    if sale.status == SaleStatus.EJECUTADO:
                        try:
                            sales_services.execute_sale(sale, user=request.user, ip=request.META.get('REMOTE_ADDR'))
                        except Exception as e:
                            messages.error(request, str(e))

                    messages.success(request, 'Sale created')
                    return redirect(reverse('sales:fast_sale'))
            except Exception as e:
                messages.error(request, f'Error creating sale: {e}')
        else:
            messages.error(request, 'Please fix errors below')
    else:
        sale_form = SaleForm(initial={'customer': _get_default_customer(), 'status': SaleStatus.PROFORMA})
        formset = SaleItemFormSet()
        quick_customer = QuickCustomerForm()

    return render(request, 'sales/fast_sale.html', {'sale_form': sale_form, 'formset': formset, 'quick_customer': quick_customer})


def sale_list(request):
    q = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    qs = Sale.objects.select_related('customer').all().order_by('-sale_date')
    if q:
        qs = qs.filter(customer__name__icontains=q)
    paginator = Paginator(qs, 25)
    pag = paginator.get_page(page)
    return render(request, 'sales/list.html', {'sales': pag})


def sale_detail(request, pk):
    sale = get_object_or_404(Sale.objects.prefetch_related('items', 'payments', 'audits'), pk=pk)
    return render(request, 'sales/detail.html', {'sale': sale})


def sale_execute(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    try:
        sales_services.execute_sale(sale, user=request.user, ip=request.META.get('REMOTE_ADDR'))
        return redirect('sales:sale_detail', pk=pk)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('sales:sale_detail', pk=pk)


def sale_reserve(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    try:
        sales_services.reserve_sale(sale, user=request.user, ip=request.META.get('REMOTE_ADDR'))
        return redirect('sales:sale_detail', pk=pk)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('sales:sale_detail', pk=pk)


def sale_cancel(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    try:
        sales_services.cancel_sale(sale, user=request.user, ip=request.META.get('REMOTE_ADDR'))
        return redirect('sales:sale_detail', pk=pk)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('sales:sale_detail', pk=pk)


def sale_payment(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        notes = request.POST.get('notes', '')
        try:
            # register payment and record cash movement
            cash_services.register_sale_payment(sale, amount, user=request.user, ip=request.META.get('REMOTE_ADDR'), notes=notes)
            messages.success(request, 'Payment registered')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('sales:sale_detail', pk=pk)


def _render_sale_document(request, sale, template_name, filename):
    html = render_to_string(template_name, {'sale': sale, 'request': request})
    # Try to generate PDF using utils_pdf
    try:
        pdf_bytes = utils_pdf.render_pdf_from_html(html)
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = f'inline; filename="{filename}"'
        return resp
    except Exception:
        # fallback to HTML
        return HttpResponse(html)


def sale_proforma_pdf(request, pk):
    sale = get_object_or_404(Sale.objects.prefetch_related('items'), pk=pk)
    return _render_sale_document(request, sale, 'sales/pdf/proforma.html', f'proforma_{sale.number or sale.pk}.pdf')


def sale_delivery_pdf(request, pk):
    sale = get_object_or_404(Sale.objects.prefetch_related('items'), pk=pk)
    return _render_sale_document(request, sale, 'sales/pdf/delivery_note.html', f'delivery_{sale.number or sale.pk}.pdf')


def sale_receipt_pdf(request, pk):
    sale = get_object_or_404(Sale.objects.prefetch_related('items', 'payments'), pk=pk)
    return _render_sale_document(request, sale, 'sales/pdf/receipt.html', f'receipt_{sale.number or sale.pk}.pdf')
