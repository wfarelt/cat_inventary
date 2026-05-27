from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from . import services as cash_services


def _user_is_cashier(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    groups = {g.name.lower() for g in user.groups.all()}
    return 'cashier' in groups or 'caja' in groups


@login_required
def open_cash_view(request):
    if not _user_is_cashier(request.user):
        messages.error(request, 'Permission denied')
        return redirect(reverse('cash:movements_list'))
    if request.method == 'POST':
        amount = request.POST.get('opening_amount', 0)
        try:
            cash_services.open_cash(amount, opened_by=request.user)
            messages.success(request, 'Cash opened')
            return redirect(reverse('cash:movements_list'))
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'cash/open.html')


@login_required
def close_cash_view(request):
    if not _user_is_cashier(request.user):
        messages.error(request, 'Permission denied')
        return redirect(reverse('cash:movements_list'))
    op = cash_services.get_current_opening()
    if not op:
        messages.error(request, 'No open cash')
        return redirect(reverse('cash:open_cash'))
    if request.method == 'POST':
        real = request.POST.get('real_amount', 0)
        try:
            cash_services.close_cash(real, closed_by=request.user)
            messages.success(request, 'Cash closed')
            return redirect(reverse('cash:movements_list'))
        except Exception as e:
            messages.error(request, str(e))
    expected = cash_services.get_expected_amount(op)
    return render(request, 'cash/close.html', {'opening': op, 'expected': expected})


@login_required
def movements_list(request):
    movements = cash_services.get_current_opening() and __import__('cash.models', fromlist=['CashMovement']).CashMovement.objects.order_by('-created_at')[:200]
    return render(request, 'cash/movements.html', {'movements': movements})


@login_required
def closing_report(request):
    if not _user_is_cashier(request.user):
        messages.error(request, 'Permission denied')
        return redirect(reverse('cash:movements_list'))
    op = cash_services.get_current_opening()
    if not op:
        messages.error(request, 'No open cash')
        return redirect(reverse('cash:open_cash'))
    report = cash_services.generate_closing_report(op)
    return render(request, 'cash/closing_report.html', {'report': report})
