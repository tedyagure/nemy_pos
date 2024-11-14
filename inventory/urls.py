from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='list'),
    path('categories/', views.categories, name='categories'),
    path('add/', views.add_item, name='add_item'),
    path('edit/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete/<int:pk>/', views.delete_item, name='delete_item'),
    path('<int:pk>/history/', views.item_history, name='item_history'),
    path('api/adjust/', views.adjust_stock, name='adjust_stock'),
    path('api/reorder-level/', views.set_reorder_level, name='set_reorder_level'),
] 