from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_update, name='product_update'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_update, name='category_update'),
    path('rental-machines/', views.rental_machine_list, name='rental_machine_list'),
    path('rental-machines/<int:machine_id>/', views.rental_machine_detail, name='rental_machine_detail'),
    path('rental-machines/create/', views.rental_machine_create, name='rental_machine_create'),
    path('rental-machines/<int:machine_id>/edit/', views.rental_machine_update, name='rental_machine_update'),
] 