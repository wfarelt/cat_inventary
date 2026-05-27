from django.shortcuts import render, get_object_or_404
from .models import Company


def company_detail(request):
    company = Company.objects.first()
    return render(request, 'company/detail.html', {'company': company})
