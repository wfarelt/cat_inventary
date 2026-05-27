from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from core.permissions import is_admin
from .models import User




@permission_required('auth.view_user', raise_exception=True)
def user_list(request):
    qs = User.objects.all().order_by('username')
    return render(request, 'users/list.html', {'users': qs})
