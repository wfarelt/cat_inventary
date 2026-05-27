from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from core.permissions import is_admin
from .models import SiteConfiguration
from .forms import SiteConfigurationForm




@permission_required('settings_app.change_siteconfiguration', raise_exception=True)
def settings_list(request):
    qs = SiteConfiguration.objects.all().order_by('key')
    return render(request, 'settings_app/list.html', {'items': qs})


@permission_required('settings_app.change_siteconfiguration', raise_exception=True)
def settings_edit(request, pk=None):
    if pk:
        item = get_object_or_404(SiteConfiguration, pk=pk)
    else:
        item = None

    if request.method == 'POST':
        form = SiteConfigurationForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('settings_list')
    else:
        form = SiteConfigurationForm(instance=item)
    return render(request, 'settings_app/form.html', {'form': form})
