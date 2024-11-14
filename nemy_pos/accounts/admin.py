from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser',
                      'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'user_type'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Customer Admin
    """
    list_display = ('name', 'customer_type', 'phone', 'email', 'credit_allowed')
    list_filter = ('customer_type', 'credit_allowed')
    search_fields = ('name', 'email', 'phone')
    fieldsets = (
        (None, {
            'fields': ('name', 'customer_type', 'contact_person')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Credit Information', {
            'fields': ('credit_allowed', 'credit_limit', 
                      'negotiation_percentage')
        }),
    )
