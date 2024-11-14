from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.rental_list, name='list'),
    path('create/', views.create_rental, name='create'),
    path('return/<int:pk>/', views.return_rental, name='return'),
    path('receipt/<int:pk>/', views.rental_receipt, name='receipt'),
    path('reports/', views.rental_reports, name='reports'),
] 