
from django import forms
from .models import Product, Category, RentalMachine

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'part_number', 'current_stock']
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class RentalMachineForm(forms.ModelForm):
    class Meta:
        model = RentalMachine
        fields = ['name', 'is_available']