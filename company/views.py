from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Company
from .forms import CompanyForm


def is_admin(user):
    return user.is_active and user.is_superuser


def company_list(request):
    qs = Company.objects.all().order_by('name')
    return render(request, 'company/list.html', {'companies': qs})


@user_passes_test(is_admin)
def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_list')
    else:
        form = CompanyForm()
    return render(request, 'company/form.html', {'form': form, 'title': 'Crear Empresa'})


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    return render(request, 'company/detail.html', {'company': company})


@user_passes_test(is_admin)
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'company/form.html', {'form': form, 'title': 'Editar Empresa'})


@user_passes_test(is_admin)
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.is_active = False
        company.save()
        return redirect('company_list')
    return render(request, 'company/confirm_delete.html', {'company': company})
