from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import SiteConfiguration
from .forms import SiteConfigurationForm


def is_admin(user):
    return user.is_active and user.is_superuser


@user_passes_test(is_admin)
def settings_list(request):
    qs = SiteConfiguration.objects.all().order_by('key')
    return render(request, 'settings_app/list.html', {'items': qs})


@user_passes_test(is_admin)
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
