from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .models import Quotation, QuotationItem, Sale, SaleItem, QuotationTemplate, QuotationApproval
from .serializers import (QuotationSerializer, QuotationItemSerializer,
                         SaleSerializer, SaleItemSerializer)
from .services import QuotationService, EmailService
import os
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User
from .forms import QuotationForm, SaleForm

# Create your views here.

class QuotationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Quotations
    Handles quotation generation and management
    """
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Generate reference number when creating quotation"""
        reference_number = QuotationService.generate_reference_number()
        serializer.save(
            reference_number=reference_number,
            created_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def convert_to_sale(self, request, pk=None):
        """Convert quotation to sale"""
        quotation = self.get_object()
        
        # Create sale from quotation
        sale = Sale.objects.create(
            customer=quotation.customer,
            created_by=request.user,
            quotation=quotation
        )
        
        # Copy items from quotation to sale
        for quote_item in quotation.quotationitem_set.all():
            SaleItem.objects.create(
                sale=sale,
                product=quote_item.product,
                quantity=quote_item.quantity,
                unit_price=quote_item.unit_price,
                discount_percentage=quote_item.discount_percentage
            )
        
        return Response({'sale_id': sale.id})

    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF for quotation"""
        quotation = self.get_object()
        template = QuotationTemplate.objects.filter(is_default=True).first()
        
        if not template:
            return Response(
                {'error': 'No default template found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        pdf_path = QuotationService.generate_pdf(quotation, template)
        
        return Response({
            'status': 'success',
            'pdf_url': pdf_path
        })

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download generated PDF"""
        quotation = self.get_object()
        pdf_path = f'quotations/quotation_{quotation.reference_number}.pdf'
        full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
        
        if not os.path.exists(full_path):
            return Response(
                {'error': 'PDF not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            open(full_path, 'rb'),
            as_attachment=True,
            filename=f'quotation_{quotation.reference_number}.pdf'
        )

    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Send quotation via email"""
        quotation = self.get_object()
        additional_message = request.data.get('message', '')
        
        # Generate PDF if not exists
        template = QuotationTemplate.objects.filter(is_default=True).first()
        pdf_path = QuotationService.generate_pdf(quotation, template)
        
        # Send email
        try:
            EmailService.send_quotation_email(
                quotation, 
                pdf_path, 
                additional_message
            )
            return Response({'status': 'email sent'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def request_approval(self, request, pk=None):
        """Request approval for quotation"""
        quotation = self.get_object()
        approver_id = request.data.get('approver_id')
        
        try:
            approver = User.objects.get(id=approver_id)
            QuotationApproval.objects.create(
                quotation=quotation,
                approver=approver
            )
            return Response({'status': 'approval requested'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Approver not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve or reject quotation"""
        quotation = self.get_object()
        approval = quotation.quotationapproval_set.first()
        
        if not approval:
            return Response(
                {'error': 'No approval request found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        approval.status = request.data.get('status', 'APPROVED')
        approval.comments = request.data.get('comments', '')
        approval.save()
        
        return Response({'status': 'quotation processed'})

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple quotations at once"""
        quotations_data = request.data.get('quotations', [])
        created_quotations = []
        
        try:
            with transaction.atomic():
                for quotation_data in quotations_data:
                    # Generate reference number
                    reference_number = QuotationService.generate_reference_number()
                    
                    # Create quotation
                    quotation = Quotation.objects.create(
                        reference_number=reference_number,
                        customer_id=quotation_data['customer_id'],
                        created_by=request.user,
                        valid_until=quotation_data['valid_until']
                    )
                    
                    # Create items
                    for item_data in quotation_data.get('items', []):
                        QuotationItem.objects.create(
                            quotation=quotation,
                            **item_data
                        )
                    
                    created_quotations.append(quotation)
                    
            serializer = self.get_serializer(created_quotations, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Sales
    Handles sales transactions and payments
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process payment for sale"""
        sale = self.get_object()
        # Add payment processing logic here
        return Response({'status': 'payment processed'})

def quotation_list(request):
    quotations = Quotation.objects.all()
    return render(request, 'sales/quotation_list.html', {'quotations': quotations})

def quotation_detail(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    return render(request, 'sales/quotation_detail.html', {'quotation': quotation})

def quotation_create(request):
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quotation_list')
    else:
        form = QuotationForm()
    return render(request, 'sales/quotation_form.html', {'form': form})

def quotation_update(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    if request.method == 'POST':
        form = QuotationForm(request.POST, instance=quotation)
        if form.is_valid():
            form.save()
            return redirect('quotation_list')
    else:
        form = QuotationForm(instance=quotation)
    return render(request, 'sales/quotation_form.html', {'form': form, 'quotation': quotation})

def sale_list(request):
    sales = Sale.objects.all()
    return render(request, 'sales/sale_list.html', {'sales': sales})

def sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'sales/sale_detail.html', {'sale': sale})

def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sale_list')
    else:
        form = SaleForm()
    return render(request, 'sales/sale_form.html', {'form': form})

def sale_update(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sales/sale_form.html', {'form': form, 'sale': sale})
