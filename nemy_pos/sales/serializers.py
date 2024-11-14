from rest_framework import serializers
from .models import Quotation, QuotationItem, Sale, SaleItem

class QuotationItemSerializer(serializers.ModelSerializer):
    """Serializer for individual items in quotations"""
    class Meta:
        model = QuotationItem
        fields = '__all__'

class QuotationSerializer(serializers.ModelSerializer):
    """
    Serializer for quotations with nested items
    Handles quotation generation and status tracking
    """
    items = QuotationItemSerializer(many=True, read_only=True, source='quotationitem_set')

    class Meta:
        model = Quotation
        fields = '__all__'

class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer for individual items in sales"""
    class Meta:
        model = SaleItem
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    """
    Serializer for sales with nested items
    Includes credit handling and payment tracking
    """
    items = SaleItemSerializer(many=True, read_only=True, source='saleitem_set')

    class Meta:
        model = Sale
        fields = '__all__' 