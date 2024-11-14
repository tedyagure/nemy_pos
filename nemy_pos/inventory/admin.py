from django.contrib import admin
from .models import Product, Category, RentalMachine
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_number', 'current_stock')
    search_fields = ('name', 'part_number')
    list_filter = ('category',) 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)   

@admin.register(RentalMachine)
class RentalMachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_available')
    search_fields = ('name',) 
