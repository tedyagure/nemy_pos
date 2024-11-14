import os
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from decimal import Decimal
from django.core.mail import EmailMessage

class QuotationService:
    """
    Service class for handling quotation-related operations
    """
    
    @staticmethod
    def calculate_item_total(quantity, unit_price, discount_percentage):
        """Calculate total for a single item with discount"""
        subtotal = Decimal(quantity) * Decimal(unit_price)
        discount = subtotal * (Decimal(discount_percentage) / 100)
        return subtotal - discount

    @staticmethod
    def calculate_quotation_total(items):
        """Calculate total for entire quotation"""
        total = Decimal('0.00')
        for item in items:
            total += QuotationService.calculate_item_total(
                item.quantity,
                item.unit_price,
                item.discount_percentage
            )
        return total

    @staticmethod
    def generate_reference_number():
        """Generate unique quotation reference number"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        return f'QT-{timestamp}'

    @staticmethod
    def generate_pdf(quotation, template):
        """Generate PDF quotation"""
        # Prepare context for template
        context = {
            'quotation': quotation,
            'template': template,
            'company_name': 'Your Company Name',
            'items': quotation.quotationitem_set.all(),
            'total': QuotationService.calculate_quotation_total(
                quotation.quotationitem_set.all()
            ),
            'generated_date': datetime.now(),
        }

        # Render HTML
        html_string = render_to_string('sales/quotation_template.html', context)

        # Generate PDF
        output_file = f'quotation_{quotation.reference_number}.pdf'
        output_path = os.path.join(settings.MEDIA_ROOT, 'quotations', output_file)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create PDF
        with open(output_path, 'wb') as pdf_file:
            pisa.CreatePDF(html_string, dest=pdf_file)

        return f'quotations/{output_file}' 

class EmailService:
    """
    Service for handling email operations
    """
    @staticmethod
    def send_quotation_email(quotation, pdf_path, additional_message=None):
        """Send quotation email to customer"""
        subject = f'Quotation #{quotation.reference_number} from Your Company'
        
        # Render email template
        context = {
            'quotation': quotation,
            'additional_message': additional_message,
            'company_name': 'Your Company Name'
        }
        email_body = render_to_string('sales/email/quotation_email.html', context)
        
        # Create email
        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email='your@company.com',
            to=[quotation.customer.email],
            reply_to=['sales@company.com']
        )
        
        # Attach PDF
        with open(pdf_path, 'rb') as pdf:
            email.attach(
                f'Quotation_{quotation.reference_number}.pdf',
                pdf.read(),
                'application/pdf'
            )
            
        return email.send() 