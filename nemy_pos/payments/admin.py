from django.contrib import admin
from .models import Payment

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('sale', 'amount', 'payment_method', 'payment_date')
    search_fields = ('sale__reference_number',)
    list_filter = ('payment_method',)
