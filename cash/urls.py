from django.urls import path
from . import views

app_name = 'cash'

urlpatterns = [
    path('open/', views.open_cash_view, name='open_cash'),
    path('close/', views.close_cash_view, name='close_cash'),
    path('movements/', views.movements_list, name='movements_list'),
    path('closing-report/', views.closing_report, name='closing_report'),
]
