from django.urls import path
from django.shortcuts import redirect
from . import views


def index(request):
    return redirect('admin:index')

urlpatterns = [
    path('', index, name='settings_index'),
    path('list/', views.settings_list, name='settings_list'),
    path('edit/', views.settings_edit, name='settings_edit'),
    path('edit/<int:pk>/', views.settings_edit, name='settings_edit'),
]
