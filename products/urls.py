from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.product_create, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('search/autocomplete/', views.product_autocomplete, name='product_autocomplete'),
    path('import/', views.product_import, name='product_import'),
    path('import/confirm/', views.product_import_confirm, name='product_import_confirm'),
    path('images/upload/', views.upload_images_zip, name='upload_images_zip'),
    # Product kits
        path('import/selection/', views.product_import_selection, name='product_import_selection'),
    path('kits/', views.kit_list, name='kit_list'),
    path('kits/add/', views.kit_create, name='kit_create'),
    path('kits/<int:pk>/', views.kit_detail, name='kit_detail'),
    path('kits/<int:pk>/edit/', views.kit_edit, name='kit_edit'),
    path('kits/<int:pk>/add-item/', views.kit_add_item, name='kit_add_item'),
    path('kits/<int:pk>/remove-item/<int:item_pk>/', views.kit_remove_item, name='kit_remove_item'),
    # Categories CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
