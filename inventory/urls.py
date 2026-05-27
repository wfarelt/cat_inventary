from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.movements_list, name='movements_list'),
    path('create/', views.movement_create, name='movement_create'),
    path('kardex/', views.kardex_view, name='kardex'),
]
