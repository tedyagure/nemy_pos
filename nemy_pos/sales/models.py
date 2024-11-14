from django.db import models
from accounts.models import User, Customer

class Quotation(models.Model):
    """
    Handles quotation requests and generation
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )

    reference_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Adjust as necessary
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    valid_until = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotations'

class QuotationItem(models.Model):
    """
    Individual items in a quotation
    """
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = 'quotation_items'

class Sale(models.Model):
    """
    Handles all sales transactions
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    reference_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Adjust as necessary
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_credit = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales'

class SaleItem(models.Model):
    """
    Individual items in a sale
    """
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = 'sale_items'

class QuotationTemplate(models.Model):
    """
    Model for storing quotation templates
    """
    name = models.CharField(max_length=100)
    header_text = models.TextField(help_text="Company header information")
    footer_text = models.TextField(help_text="Terms and conditions, etc.")
    logo = models.ImageField(upload_to='quotation_templates/', null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotation_templates'

    def save(self, *args, **kwargs):
        # Ensure only one default template exists
        if self.is_default:
            QuotationTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class QuotationApproval(models.Model):
    """
    Model for tracking quotation approvals
    """
    APPROVAL_STATUS = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    approver = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='PENDING')
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotation_approvals'
