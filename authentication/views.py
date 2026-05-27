from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from products.models import Product, Category, ProductKit
from company.models import Company
from users.models import User
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime


def _last_n_months(n):
    today = timezone.now().date().replace(day=1)
    months = []
    year = today.year
    month = today.month
    for i in range(n-1, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    return months


from django.contrib.auth.decorators import login_required


@login_required
def dashboard_data(request):
    # category distribution
    cats = Category.objects.all().order_by('name')
    cat_labels = [c.name for c in cats]
    cat_counts = [c.products.count() for c in cats]

    # products added per month (last 6 months)
    months = _last_n_months(6)
    labels = [f"{m:02d}/{y}" for (y, m) in months]
    counts = []
    for (y, m) in months:
        start = datetime(y, m, 1)
        if m == 12:
            end = datetime(y+1, 1, 1)
        else:
            end = datetime(y, m+1, 1)
        cnt = Product.objects.filter(created_at__gte=start, created_at__lt=end).count()
        counts.append(cnt)

    return JsonResponse({
        'category_labels': cat_labels,
        'category_counts': cat_counts,
        'trend_labels': labels,
        'trend_counts': counts,
    })


@login_required
def dashboard(request):
    product_count = Product.objects.count()
    category_count = Category.objects.count()
    recent_products = Product.objects.select_related('category').order_by('-pk')[:5]
    kit_count = ProductKit.objects.count()
    recent_kits = ProductKit.objects.order_by('-pk')[:5]
    images_count = Product.objects.filter(image__isnull=False).exclude(image='').count()
    company_count = Company.objects.count()
    user_count = User.objects.count()
    return render(request, 'dashboard.html', {
        'product_count': product_count,
        'category_count': category_count,
        'recent_products': recent_products,
        'kit_count': kit_count,
        'recent_kits': recent_kits,
        'images_count': images_count,
        'company_count': company_count,
        'user_count': user_count,
    })
