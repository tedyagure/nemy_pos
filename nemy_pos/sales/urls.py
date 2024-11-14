from django.urls import path
from . import views

urlpatterns = [
    path('quotations/', views.quotation_list, name='quotation_list'),
    path('quotations/<int:quotation_id>/', views.quotation_detail, name='quotation_detail'),
    path('quotations/create/', views.quotation_create, name='quotation_create'),
    path('quotations/<int:quotation_id>/edit/', views.quotation_update, name='quotation_update'),
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/<int:sale_id>/edit/', views.sale_update, name='sale_update'),
] 