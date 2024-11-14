from django.contrib import admin
from .models import (QuotationTemplate, Quotation, QuotationItem, 
                    QuotationApproval)

@admin.register(QuotationTemplate)
class QuotationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for quotation templates"""
    list_display = ['name', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'is_default', 'logo')
        }),
        ('Content', {
            'fields': ('header_text', 'footer_text'),
            'classes': ('wide',)
        })
    )

class QuotationItemInline(admin.TabularInline):
    """Inline admin for quotation items"""
    model = QuotationItem
    extra = 1

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    """Admin interface for quotations"""
    list_display = ['reference_number', 'customer', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reference_number', 'customer__name']
    inlines = [QuotationItemInline]
    
    readonly_fields = ['reference_number']
    
    fieldsets = (
        (None, {
            'fields': ('reference_number', 'customer', 'status')
        }),
        ('Validity', {
            'fields': ('valid_until',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )

@admin.register(QuotationApproval)
class QuotationApprovalAdmin(admin.ModelAdmin):
    """Admin interface for quotation approvals"""
    list_display = ['quotation', 'approver', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['quotation__reference_number', 'approver__username']
