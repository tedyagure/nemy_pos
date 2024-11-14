from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (Category, Product, ProductPrice, RentalMachine, 
                    TechnicianCheckout, CheckoutItem, StockMovement)
from .serializers import (CategorySerializer, ProductSerializer, 
                         ProductPriceSerializer, RentalMachineSerializer,
                         TechnicianCheckoutSerializer, CheckoutItemSerializer,
                         StockMovementSerializer)
from .filters import ProductFilter, RentalMachineFilter
from .permissions import IsAdmin, IsTechnician, IsOwnerOrAdmin
from rest_framework.decorators import action
from .forms import ProductForm, CategoryForm, RentalMachineForm

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product with filtering and search
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['name', 'part_number', 'description']
    ordering_fields = ['name', 'current_stock', 'created_at']

    def get_permissions(self):
        """
        Custom permissions based on action
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust stock levels with movement tracking"""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        # Create stock movement record
        StockMovement.objects.create(
            product=product,
            movement_type='ADJUSTMENT',
            quantity=quantity,
            created_by=request.user,
            reference_number=f'ADJ-{product.id}'
        )
        
        product.current_stock += quantity
        product.save()
        return Response({'status': 'stock adjusted'})

    @action(detail=True, methods=['get'])
    def stock_movements(self, request, pk=None):
        """Get stock movement history for a product"""
        product = self.get_object()
        movements = StockMovement.objects.filter(product=product)
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product Categories
    Handles CRUD operations for product categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class RentalMachineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RentalMachine
    """
    queryset = RentalMachine.objects.all()
    serializer_class = RentalMachineSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = RentalMachineFilter

    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Toggle machine availability status"""
        machine = self.get_object()
        machine.is_available = not machine.is_available
        machine.save()
        return Response({'status': 'availability updated'})

class TechnicianCheckoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Technician Checkouts
    Manages part checkouts and returns
    """
    queryset = TechnicianCheckout.objects.all()
    serializer_class = TechnicianCheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def return_items(self, request, pk=None):
        """Handle return of checked out items"""
        checkout = self.get_object()
        items_return = request.data.get('items', [])
        
        for item in items_return:
            checkout_item = CheckoutItem.objects.get(
                checkout=checkout, 
                id=item['id']
            )
            checkout_item.returned_quantity = item['returned_quantity']
            checkout_item.save()
            
            # Update stock
            if checkout_item.returned_quantity > 0:
                StockMovement.objects.create(
                    product=checkout_item.product,
                    movement_type='RETURN',
                    quantity=checkout_item.returned_quantity,
                    reference_number=f'RET-{checkout.id}',
                    created_by=request.user
                )
        
        return Response({'status': 'items returned'})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'inventory/product_detail.html', {'product': product})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})

def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'product': product})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    return render(request, 'inventory/category_detail.html', {'category': category})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form})

def category_update(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {'form': form, 'category': category})

def rental_machine_list(request):
    rental_machines = RentalMachine.objects.all()
    return render(request, 'inventory/rental_machine_list.html', {'rental_machines': rental_machines})

def rental_machine_detail(request, machine_id):
    machine = get_object_or_404(RentalMachine, id=machine_id)
    return render(request, 'inventory/rental_machine_detail.html', {'machine': machine})

def rental_machine_create(request):
    if request.method == 'POST':
        form = RentalMachineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rental_machine_list')
    else:
        form = RentalMachineForm()
    return render(request, 'inventory/rental_machine_form.html', {'form': form})

def rental_machine_update(request, machine_id):
    machine = get_object_or_404(RentalMachine, id=machine_id)
    if request.method == 'POST':
        form = RentalMachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            return redirect('rental_machine_list')
    else:
        form = RentalMachineForm(instance=machine)
    return render(request, 'inventory/rental_machine_form.html', {'form': form, 'machine': machine})

# ... Continue with other views ...
