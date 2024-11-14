from django.db import models
from sales.models import Sale
from rentals.models import RentalAgreement
from accounts.models import User

class Payment(models.Model):
    """
    Handles all payments in the system
    """
    PAYMENT_TYPES = (
        ('SALE', 'Sale Payment'),
        ('RENTAL', 'Rental Payment'),
        ('TECHNICIAN', 'Technician Payment'),
    )
    
    PAYMENT_METHODS = (
        ('MPESA', 'M-Pesa'),
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    reference_number = models.CharField(max_length=20, unique=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True)
    rental = models.ForeignKey(RentalAgreement, on_delete=models.SET_NULL, null=True, blank=True)
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)  # For M-Pesa transaction ID
    payment_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'

class MPesaTransaction(models.Model):
    """
    Handles M-Pesa specific transaction details
    """
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    mpesa_receipt_number = models.CharField(max_length=50)
    transaction_date = models.DateTimeField()
    response_data = models.JSONField()  # Stores the full M-Pesa response

    class Meta:
        db_table = 'mpesa_transactions'
