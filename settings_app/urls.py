from django.urls import path
from django.shortcuts import redirect

def index(request):
    return redirect('admin:index')

urlpatterns = [
    path('', index, name='settings_index'),
]
