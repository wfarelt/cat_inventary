from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from . import services


@login_required
def index(request):
    # simple range via ?range=today|yesterday|week|month|custom
    range_key = request.GET.get('range', 'today')
    start = request.GET.get('start')
    end = request.GET.get('end')
    # parse start/end if provided
    from datetime import datetime
    s = None; e = None
    try:
        if start:
            s = datetime.strptime(start, '%Y-%m-%d').date()
        if end:
            e = datetime.strptime(end, '%Y-%m-%d').date()
    except Exception:
        s = e = None

    metrics = services.get_dashboard_metrics(request.user, range_key=range_key, start=s, end=e)
    return render(request, 'dashboard/index.html', {'metrics': metrics})
