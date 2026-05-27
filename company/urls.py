from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_detail, name='company_detail'),
]
