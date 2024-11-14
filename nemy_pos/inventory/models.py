from django.db import models
from accounts.models import User, Customer

class Category(models.Model):
    """
    Product categories for better organization
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

class Product(models.Model):
    """
    Product model for spare parts inventory
    """
    name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    shelf_location = models.CharField(max_length=50)
    minimum_stock = models.IntegerField(default=0)
    current_stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

class ProductPrice(models.Model):
    """
    Different pricing for different customer types
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer_type = models.CharField(max_length=20, choices=Customer.CUSTOMER_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'product_prices'
        unique_together = ['product', 'customer_type']

class RentalMachine(models.Model):
    """
    Coffee machines and grinders available for rent
    """
    RENTAL_TYPES = (
        ('COFFEE_MACHINE', 'Coffee Machine'),
        ('GRINDER', 'Grinder'),
    )

    name = models.CharField(max_length=200)
    machine_type = models.CharField(max_length=20, choices=RENTAL_TYPES)
    serial_number = models.CharField(max_length=50, unique=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    quarterly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'rental_machines'

class TechnicianCheckout(models.Model):
    """
    Handles parts checkout by technicians
    """
    STATUS_CHOICES = (
        ('CHECKED_OUT', 'Checked Out'),
        ('RETURNED', 'Returned'),
        ('USED', 'Used'),
        ('OVERDUE', 'Overdue'),
    )

    technician = models.ForeignKey(User, on_delete=models.CASCADE)
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CHECKED_OUT')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'technician_checkouts'

class CheckoutItem(models.Model):
    """
    Individual items in a technician checkout
    """
    checkout = models.ForeignKey(TechnicianCheckout, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    returned_quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'checkout_items'

class StockMovement(models.Model):
    """
    Tracks all stock movements (in/out)
    """
    MOVEMENT_TYPES = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('RETURN', 'Return'),
        ('ADJUSTMENT', 'Adjustment'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference_number = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_movements'
