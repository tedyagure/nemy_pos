from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('create/', views.create_payment, name='create'),
    path('receipt/<int:pk>/', views.payment_receipt, name='receipt'),
    path('reports/', views.payment_reports, name='reports'),
] 