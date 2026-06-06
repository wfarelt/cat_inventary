from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.product_create, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
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
    # Brands CRUD
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_create, name='brand_create'),
    path('brands/<int:pk>/edit/', views.brand_edit, name='brand_edit'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
    # API
    path('api/products/', views.api_product_list, name='api_product_list'),
    path('api/products/<int:pk>/', views.api_product_detail, name='api_product_detail'),
    path('api/products/import/preview/', views.api_product_import_preview, name='api_product_import_preview'),
    path('import/map/', views.product_import_map, name='product_import_map'),
    path('import/edit-cell/', views.product_import_edit_cell, name='product_import_edit_cell'),
    path('import/selection/clear/', views.product_import_clear_selection, name='product_import_clear_selection'),
    path('images/manager/', views.image_manager, name='image_manager'),
    path('images/<int:pk>/unassign/', views.image_unassign, name='image_unassign'),
    path('bulk/', views.product_bulk_action, name='product_bulk_action'),
    path('bulk/selection/', views.product_bulk_selection, name='product_bulk_selection'),
    path('bulk/selection/clear/', views.product_bulk_clear_selection, name='product_bulk_clear_selection'),
]
