from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import User


def is_admin(user):
    return user.is_active and user.is_superuser


@user_passes_test(is_admin)
def user_list(request):
    qs = User.objects.all().order_by('username')
    return render(request, 'users/list.html', {'users': qs})
