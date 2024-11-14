from rest_framework import serializers
from .models import (Category, Product, ProductPrice, RentalMachine, 
                    TechnicianCheckout, CheckoutItem, StockMovement)

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    class Meta:
        model = Category
        fields = '__all__'

class ProductPriceSerializer(serializers.ModelSerializer):
    """Serializer for product pricing based on customer type"""
    class Meta:
        model = ProductPrice
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for products with nested pricing information
    Includes stock levels and location details
    """
    prices = ProductPriceSerializer(many=True, read_only=True, source='productprice_set')
    
    class Meta:
        model = Product
        fields = '__all__'

class RentalMachineSerializer(serializers.ModelSerializer):
    """Serializer for rental machines with pricing details"""
    class Meta:
        model = RentalMachine
        fields = '__all__'

class CheckoutItemSerializer(serializers.ModelSerializer):
    """Serializer for individual items in technician checkouts"""
    class Meta:
        model = CheckoutItem
        fields = '__all__'

class TechnicianCheckoutSerializer(serializers.ModelSerializer):
    """
    Serializer for technician checkouts with nested items
    Includes due date calculations and status tracking
    """
    items = CheckoutItemSerializer(many=True, read_only=True, source='checkoutitem_set')

    class Meta:
        model = TechnicianCheckout
        fields = '__all__'

class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for tracking stock movements"""
    class Meta:
        model = StockMovement
        fields = '__all__' 