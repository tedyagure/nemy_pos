from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sales_list, name='list'),
    path('pos/', views.pos, name='pos'),
    path('receipt/<int:pk>/', views.receipt, name='receipt'),
    path('invoice/<int:pk>/', views.invoice, name='invoice'),
    path('api/create/', views.create_sale, name='create_sale'),
    path('api/void/<int:pk>/', views.void_sale, name='void_sale'),
    path('reports/', views.reports, name='reports'),
    path('api/sales-data/', views.sales_data, name='sales_data'),
] 