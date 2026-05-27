from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.purchase_list, name='purchase_list'),
    path('create/', views.purchase_create, name='purchase_create'),
    path('<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('<int:pk>/confirm/', views.purchase_confirm, name='purchase_confirm'),
    path('<int:pk>/cancel/', views.purchase_cancel, name='purchase_cancel'),
]
