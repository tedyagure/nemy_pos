from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Extended User model to include additional fields and user types
    """
    USER_TYPES = (
        ('ADMIN', 'Administrator'),
        ('EMPLOYEE', 'Employee'),
        ('TECHNICIAN', 'Technician'),
        ('SYSTEM_ADMIN', 'System Administrator'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'users'

class Customer(models.Model):
    """
    Customer model to handle different types of customers and their pricing
    """
    CUSTOMER_TYPES = (
        ('BUSINESS', 'Business'),
        ('COMPANY', 'Company'),
        ('INDIVIDUAL', 'Individual'),
    )

    name = models.CharField(max_length=100)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    credit_allowed = models.BooleanField(default=False)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    negotiation_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
