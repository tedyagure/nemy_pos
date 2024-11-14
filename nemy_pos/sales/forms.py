from django import forms
from .models import Quotation, Sale

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['reference_number', 'customer', 'total_amount']  # Adjust fields as necessary

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['reference_number', 'customer', 'total_amount']  # Adjust fields as necessary