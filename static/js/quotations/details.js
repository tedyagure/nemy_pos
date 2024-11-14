class QuotationDetails {
    constructor() {
        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

        // Initialize modals
        this.sendModal = new bootstrap.Modal(document.getElementById('sendQuotationModal'));
        this.convertModal = new bootstrap.Modal(document.getElementById('convertToSaleModal'));
    }

    setupEventListeners() {
        // Send quotation form
        document.getElementById('sendQuotationForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendQuotation();
        });

        // Convert to sale form
        document.getElementById('convertToSaleForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.convertToSale();
        });
    }

    async sendQuotation() {
        const form = document.getElementById('sendQuotationForm');
        const formData = new FormData(form);
        const quotationId = form.dataset.quotationId;

        try {
            const response = await fetch(`/api/quotations/${quotationId}/send/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Failed to send quotation');

            this.sendModal.hide();
            this.showNotification('Quotation sent successfully', 'success');
            this.refreshTimeline();

        } catch (error) {
            this.showNotification('Error sending quotation: ' + error.message, 'error');
        }
    }

    async convertToSale() {
        const form = document.getElementById('convertToSaleForm');
        const formData = new FormData(form);
        const quotationId = form.dataset.quotationId;

        try {
            const response = await fetch(`/api/quotations/${quotationId}/convert/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Failed to convert quotation');

            const data = await response.json();
            this.convertModal.hide();
            this.showNotification('Quotation converted to sale successfully', 'success');
            
            // Redirect to the new sale
            window.location.href = `/sales/${data.sale_id}/`;

        } catch (error) {
            this.showNotification('Error converting quotation: ' + error.message, 'error');
        }
    }

    async downloadPDF(quotationId) {
        try {
            const response = await fetch(`/api/quotations/${quotationId}/pdf/`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `quotation-${quotationId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            this.showNotification('Error downloading PDF: ' + error.message, 'error');
        }
    }

    async refreshTimeline() {
        try {
            const quotationId = document.querySelector('[data-quotation-id]').dataset.quotationId;
            const response = await fetch(`/api/quotations/${quotationId}/timeline/`);
            const activities = await response.json();
            
            const timeline = document.querySelector('.timeline');
            if (!timeline) return;

            timeline.innerHTML = activities.map(activity => `
                <div class="timeline-item">
                    <div class="timeline-icon bg-${activity.type_color}">
                        <i class="${activity.type_icon}"></i>
                    </div>
                    <div class="timeline-content">
                        <p>${activity.description}</p>
                        <small class="text-muted">
                            ${this.formatDateTime(activity.created_at)}
                        </small>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            this.showNotification('Error refreshing timeline', 'error');
        }
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showSendModal(quotationId) {
        const form = document.getElementById('sendQuotationForm');
        form.reset();
        form.dataset.quotationId = quotationId;
        this.sendModal.show();
    }

    showConvertModal(quotationId) {
        const form = document.getElementById('convertToSaleForm');
        form.reset();
        form.dataset.quotationId = quotationId;
        this.convertModal.show();
    }

    async editQuotation(quotationId) {
        try {
            // Redirect to the edit page or show edit modal
            window.location.href = `/quotations/${quotationId}/edit/`;
        } catch (error) {
            this.showNotification('Error editing quotation', 'error');
        }
    }

    async updateStatus(quotationId, status) {
        try {
            const response = await fetch(`/api/quotations/${quotationId}/status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ status })
            });

            if (!response.ok) throw new Error('Failed to update status');

            this.showNotification('Status updated successfully', 'success');
            this.refreshTimeline();
            
            // Update status badge
            const statusBadge = document.querySelector('.badge[data-status]');
            if (statusBadge) {
                statusBadge.className = `badge bg-${this.getStatusColor(status)}`;
                statusBadge.textContent = status;
            }

        } catch (error) {
            this.showNotification('Error updating status: ' + error.message, 'error');
        }
    }

    getStatusColor(status) {
        const colors = {
            draft: 'secondary',
            sent: 'primary',
            viewed: 'info',
            accepted: 'success',
            rejected: 'danger',
            expired: 'warning'
        };
        return colors[status] || 'secondary';
    }

    async deleteQuotation(quotationId) {
        if (!confirm('Are you sure you want to delete this quotation?')) return;

        try {
            const response = await fetch(`/api/quotations/${quotationId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Failed to delete quotation');

            this.showNotification('Quotation deleted successfully', 'success');
            // Redirect to quotations list
            window.location.href = '/quotations/';

        } catch (error) {
            this.showNotification('Error deleting quotation: ' + error.message, 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Implementation depends on your notification system
        console.log(`${type}: ${message}`);
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
}

// Initialize Quotation Details
document.addEventListener('DOMContentLoaded', () => {
    window.quotationDetails = new QuotationDetails();
}); 