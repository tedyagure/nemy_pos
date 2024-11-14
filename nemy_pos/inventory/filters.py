from django_filters import rest_framework as filters
from .models import Product, RentalMachine

class ProductFilter(filters.FilterSet):
    """
    Filter set for Product model
    """
    min_price = filters.NumberFilter(field_name="productprice__price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="productprice__price", lookup_expr='lte')
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'part_number': ['exact', 'icontains'],
            'current_stock': ['gt', 'lt', 'exact'],
            'shelf_location': ['exact', 'icontains'],
        }

class RentalMachineFilter(filters.FilterSet):
    """
    Filter set for RentalMachine model
    """
    class Meta:
        model = RentalMachine
        fields = {
            'machine_type': ['exact'],
            'is_available': ['exact'],
            'name': ['icontains'],
        } 