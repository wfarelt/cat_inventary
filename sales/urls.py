from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('fast/', views.fast_sale, name='fast_sale'),
    path('create/', views.fast_sale, name='sale_create'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
    path('<int:pk>/execute/', views.sale_execute, name='sale_execute'),
    path('<int:pk>/reserve/', views.sale_reserve, name='sale_reserve'),
    path('<int:pk>/cancel/', views.sale_cancel, name='sale_cancel'),
    path('<int:pk>/payment/', views.sale_payment, name='sale_payment'),
    path('<int:pk>/proforma/', views.sale_proforma_pdf, name='sale_proforma'),
    path('<int:pk>/delivery_note/', views.sale_delivery_pdf, name='sale_delivery_note'),
    path('<int:pk>/receipt/', views.sale_receipt_pdf, name='sale_receipt'),
]
