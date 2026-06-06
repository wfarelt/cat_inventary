from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum, F, Q, Count
from django.utils import timezone
from django.core.cache import cache

from django.apps import apps


def _get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


def _Product():
    return _get_model('products', 'Product')


def _Sale():
    return _get_model('sales', 'Sale')


def _SaleItem():
    return _get_model('sales', 'SaleItem')


def _StockMovement():
    return _get_model('inventory', 'StockMovement')


def _CashOpening():
    return _get_model('cash', 'CashOpening')
from django.urls import reverse


def _role_for_user(user):
    if not user.is_authenticated:
        return 'anonymous'
    if user.is_superuser:
        return 'administrator'
    role = getattr(user, 'role', None)
    if role in {'admin', 'sales', 'warehouse', 'accounting'}:
        return role
    groups = {g.name.lower() for g in user.groups.all()}
    if 'sales' in groups:
        return 'sales'
    if 'warehouse' in groups:
        return 'warehouse'
    if 'accounting' in groups:
        return 'accounting'
    return 'sales'


def get_date_range(range_key, start=None, end=None):
    today = timezone.localdate()
    if range_key == 'today':
        return today, today
    if range_key == 'yesterday':
        d = today - timedelta(days=1)
        return d, d
    if range_key == 'week':
        start = today - timedelta(days=6)
        return start, today
    if range_key == 'month':
        start = today - timedelta(days=29)
        return start, today
    if range_key == 'custom' and start and end:
        return start, end
    return today, today


def get_sales_metrics(start_date, end_date):
    # sales executed in range
    Sale = _Sale()
    if Sale is None:
        return {'sales_total': Decimal('0.00'), 'sales_count': 0}
    qs = Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date, status='EJECUTADO')
    sales_total = qs.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    sales_count = qs.count()
    return {'sales_total': sales_total, 'sales_count': sales_count}


def get_purchases_metrics(start_date, end_date):
    try:
        from purchases.models import Purchase
    except Exception:
        return {'purchases_total': Decimal('0.00'), 'purchases_count': 0}
    qs = Purchase.objects.filter(purchase_date__gte=start_date, purchase_date__lte=end_date, status='CONFIRMED')
    total = qs.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    return {'purchases_total': total, 'purchases_count': qs.count()}


def get_kpis_for_range(start_date, end_date, user):
    # top-level KPIs
    sales = get_sales_metrics(start_date, end_date)
    purchases = get_purchases_metrics(start_date, end_date)
    # cash current: current opening expected amount if exists
    CashOpening = _CashOpening()
    opening = None
    current_cash = None
    if CashOpening is not None:
        opening = CashOpening.objects.filter(status='OPEN').order_by('-opened_at').first()
        if opening:
            from cash.services import get_expected_amount
            current_cash = get_expected_amount(opening)

    # accounts receivable (only outstanding amounts)
    Sale = _Sale()
    ar_total = Decimal('0.00')
    if Sale is not None:
        ar_total = Sale.objects.filter(pending_amount__gt=0).aggregate(total=Sum('pending_amount'))['total'] or Decimal('0.00')

    # inventory alerts (use indexed fields)
    Product = _Product()
    low_stock = out_of_stock = 0
    if Product is not None:
        low_stock = Product.objects.filter(stock__lte=F('stock_min')).count()
        out_of_stock = Product.objects.filter(stock=0).count()

    # reservations due soon (next 7 days) and credits overdue
    today = timezone.localdate()
    due_reservations = 0
    credits_overdue = 0
    if Sale is not None:
        due_reservations = Sale.objects.filter(status='RESERVA', expiration_date__gte=today, expiration_date__lte=today + timedelta(days=7)).count()
        credits_overdue = Sale.objects.filter(pending_amount__gt=0, due_date__isnull=False, due_date__lt=today).count()

    return {
        'sales_total': sales['sales_total'],
        'sales_count': sales['sales_count'],
        'purchases_total': purchases['purchases_total'],
        'purchases_count': purchases['purchases_count'],
        'current_cash': current_cash,
        'accounts_receivable': ar_total,
        'low_stock_count': low_stock,
        'out_of_stock_count': out_of_stock,
        'due_reservations': due_reservations,
        'credits_overdue': credits_overdue,
    }


def get_top_products(start_date, end_date, limit=10):
    # Sum quantities sold in executed sales
    SaleItem = _SaleItem()
    Sale = _Sale()
    if SaleItem is None or Sale is None:
        return []
    items = SaleItem.objects.filter(
        sale__sale_date__gte=start_date,
        sale__sale_date__lte=end_date,
        sale__status='EJECUTADO'
    )
    qs = (
        items.values(code=F('product__code'), description=F('product__description'))
        .annotate(qty=Sum('quantity'))
        .order_by('-qty')[:limit]
    )
    return list(qs)


def get_sales_last_days(days=7):
    today = timezone.localdate()
    start = today - timedelta(days=days-1)
    Sale = _Sale()
    if Sale is None:
        qs = []
    else:
        qs = Sale.objects.filter(sale_date__gte=start, sale_date__lte=today, status='EJECUTADO').values('sale_date').annotate(total=Sum('total')).order_by('sale_date')
    # ensure all days present
    data = {str(r['sale_date']): r['total'] for r in qs}
    results = []
    for i in range(days):
        d = start + timedelta(days=i)
        results.append({'date': d.isoformat(), 'total': data.get(str(d), 0)})
    return results


def get_sales_status_distribution(start_date, end_date):
    Sale = _Sale()
    if Sale is None:
        return []
    qs = (
        Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date)
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )
    return list(qs)


def get_recent_activity(limit=20):
    acts = []
    # stock movements
    StockMovement = _StockMovement()
    if StockMovement is not None:
        sm = StockMovement.objects.select_related('product', 'created_by').order_by('-created_at')[:limit]
        for m in sm:
            user_str = getattr(m.created_by, 'username', None) if m.created_by else None
            prod_code = getattr(m.product, 'code', None) if m.product else None
            acts.append({'type': 'stock_movement', 'when': m.created_at, 'detail': f'{m.movement_type} {prod_code} {m.quantity}', 'user': user_str})
    # sales and payments
    Sale = _Sale()
    if Sale is not None:
        sales = Sale.objects.select_related('customer', 'created_by').order_by('-created_at')[:limit]
        for s in sales:
            user_str = getattr(s.created_by, 'username', None) if s.created_by else None
            acts.append({'type': 'sale', 'when': s.created_at, 'detail': f'Sale {s.number} {s.get_status_display()}', 'user': user_str})
    # sort and limit
    acts.sort(key=lambda x: x['when'], reverse=True)
    return acts[:limit]


def get_dashboard_metrics(user, range_key='today', start=None, end=None):
    start_date, end_date = get_date_range(range_key, start, end)
    role = _role_for_user(user)

    # cache per-user (or per-role for anonymous), date range
    user_key = f"u{user.pk}" if getattr(user, 'is_authenticated', False) else 'anon'
    cache_key = f"dashboard:{user_key}:{role}:{start_date.isoformat()}:{end_date.isoformat()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    kpis = get_kpis_for_range(start_date, end_date, user)
    top_products = get_top_products(start_date, end_date)
    sales_last = get_sales_last_days(7)
    status_dist = get_sales_status_distribution(start_date, end_date)
    recent = get_recent_activity()

    result = {
        'role': role,
        'start': start_date,
        'end': end_date,
        'kpis': kpis,
        'top_products': top_products,
        'sales_last': sales_last,
        'status_dist': status_dist,
        'recent_activity': recent,
    }

    # Add module-level metrics
    try:
        products_count = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
    except Exception:
        products_count = active_products = 0

    try:
        from purchases.models import Supplier, Purchase
        suppliers_count = Supplier.objects.count()
        purchases_total_all = Purchase.objects.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    except Exception:
        suppliers_count = 0
        purchases_total_all = Decimal('0.00')

    try:
        stock_movements = StockMovement.objects.count()
    except Exception:
        stock_movements = 0

    try:
        cash_openings = CashOpening.objects.count()
    except Exception:
        cash_openings = 0

    # Admin links (best-effort)
    admin_links = {
        'products': '/admin/products/product/',
        'sales': '/admin/sales/sale/',
        'purchases': '/admin/purchases/purchase/',
        'cash': '/admin/cash/cashopening/',
        'inventory': '/admin/inventory/stockmovement/',
    }

    result['modules'] = {
        'products_count': products_count,
        'active_products': active_products,
        'suppliers_count': suppliers_count,
        'purchases_total_all': purchases_total_all,
        'stock_movements': stock_movements,
        'cash_openings': cash_openings,
        'admin_links': admin_links,
    }

    # cache for short TTL to keep data fresh
    try:
        cache.set(cache_key, result, 300)
    except Exception:
        # if cache not configured or fails, ignore
        pass

    return result
