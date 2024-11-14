class QuotationManager {
    constructor() {
        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

        // Initialize modals
        this.quotationModal = new bootstrap.Modal(document.getElementById('quotationModal'));
        this.sendModal = new bootstrap.Modal(document.getElementById('sendQuotationModal'));
    }

    setupEventListeners() {
        // Search functionality
        document.getElementById('quotationSearch')?.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Status filter
        document.getElementById('statusFilter')?.addEventListener('change', (e) => {
            this.filterByStatus(e.target.value);
        });

        // Date filter
        document.getElementById('dateFilter')?.addEventListener('change', (e) => {
            this.filterByDate(e.target.value);
        });

        // Form events
        document.getElementById('quotationForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveQuotation();
        });
    }

    async handleSearch(query) {
        if (query.length < 2) return;

        try {
            const response = await fetch(`/api/quotations/search/?q=${query}`);
            const data = await response.json();
            this.updateQuotationsTable(data);
        } catch (error) {
            this.showNotification('Error searching quotations', 'error');
        }
    }

    async filterByStatus(status) {
        try {
            const response = await fetch(`/api/quotations/filter/?status=${status}`);
            const data = await response.json();
            this.updateQuotationsTable(data);
        } catch (error) {
            this.showNotification('Error filtering quotations', 'error');
        }
    }

    async filterByDate(dateRange) {
        if (dateRange === 'custom') {
            // Show date range picker
            return;
        }

        try {
            const response = await fetch(`/api/quotations/filter/?date=${dateRange}`);
            const data = await response.json();
            this.updateQuotationsTable(data);
        } catch (error) {
            this.showNotification('Error filtering quotations', 'error');
        }
    }

    createQuotation() {
        document.getElementById('quotationForm').reset();
        document.getElementById('quotationModalTitle').textContent = 'Create Quotation';
        document.getElementById('itemsList').innerHTML = '';
        this.addItemRow(); // Add first item row
        this.quotationModal.show();
    }

    addItemRow() {
        const template = document.getElementById('itemRowTemplate');
        const clone = template.content.cloneNode(true);
        document.getElementById('itemsList').appendChild(clone);

        // Setup event listeners for the new row
        const row = document.getElementById('itemsList').lastElementChild;
        this.setupItemRowEvents(row);
    }

    setupItemRowEvents(row) {
        const productSelect = row.querySelector('.product-select');
        const quantityInput = row.querySelector('.quantity-input');
        const priceInput = row.querySelector('.price-input');

        productSelect.addEventListener('change', () => {
            const option = productSelect.selectedOptions[0];
            if (option) {
                priceInput.value = option.dataset.price || '';
                this.calculateTotals();
            }
        });

        [quantityInput, priceInput].forEach(input => {
            input.addEventListener('input', () => this.calculateTotals());
        });
    }

    removeItemRow(button) {
        button.closest('.item-row').remove();
        this.calculateTotals();
    }

    calculateTotals() {
        let subtotal = 0;
        const rows = document.querySelectorAll('.item-row');
        
        rows.forEach(row => {
            const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
            const price = parseFloat(row.querySelector('.price-input').value) || 0;
            subtotal += quantity * price;
        });

        const discount = parseFloat(document.querySelector('[name="discount"]').value) || 0;
        const discountAmount = (subtotal * discount) / 100;
        const taxableAmount = subtotal - discountAmount;
        const tax = taxableAmount * 0.075; // 7.5% tax
        const total = taxableAmount + tax;

        document.getElementById('subtotal').textContent = `₦${subtotal.toFixed(2)}`;
        document.getElementById('discountAmount').textContent = `-₦${discountAmount.toFixed(2)}`;
        document.getElementById('tax').textContent = `₦${tax.toFixed(2)}`;
        document.getElementById('total').textContent = `₦${total.toFixed(2)}`;
    }

    async saveQuotation(action = 'draft') {
        const form = document.getElementById('quotationForm');
        const formData = new FormData(form);
        formData.append('action', action);

        try {
            const response = await fetch('/api/quotations/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to save quotation');

            this.quotationModal.hide();
            this.showNotification('Quotation saved successfully', 'success');
            
            if (action === 'send') {
                this.sendQuotation(await response.json());
            } else {
                this.refreshQuotations();
            }
        } catch (error) {
            this.showNotification('Error saving quotation: ' + error.message, 'error');
        }
    }

    async sendQuotation(quotationId) {
        try {
            const response = await fetch(`/api/quotations/${quotationId}/send/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Failed to send quotation');

            this.showNotification('Quotation sent successfully', 'success');
            this.refreshQuotations();
        } catch (error) {
            this.showNotification('Error sending quotation: ' + error.message, 'error');
        }
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
            this.refreshQuotations();
        } catch (error) {
            this.showNotification('Error deleting quotation: ' + error.message, 'error');
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

    updateQuotationsTable(quotations) {
        const tbody = document.querySelector('table tbody');
        if (!tbody) return;

        tbody.innerHTML = quotations.map(quotation => `
            <tr>
                <td>
                    <a href="/quotations/${quotation.id}/" class="quotation-link">
                        #${quotation.id}
                    </a>
                </td>
                <td>
                    <div class="customer-cell">
                        ${this.renderCustomerAvatar(quotation.customer)}
                        <div>
                            <h6>${quotation.customer.name}</h6>
                            <small class="text-muted">${quotation.customer.email}</small>
                        </div>
                    </div>
                </td>
                <td>${this.formatDate(quotation.created_at)}</td>
                <td>${this.formatDate(quotation.valid_until)}</td>
                <td>₦${quotation.total}</td>
                <td>
                    <span class="badge bg-${quotation.status_color}">
                        ${quotation.status}
                    </span>
                </td>
                <td>
                    ${this.renderActions(quotation)}
                </td>
            </tr>
        `).join('');
    }

    renderCustomerAvatar(customer) {
        if (customer.avatar) {
            return `<img src="${customer.avatar}" alt="${customer.name}">`;
        }
        return `
            <div class="avatar-placeholder">
                ${customer.name.charAt(0).toUpperCase()}
            </div>
        `;
    }

    renderActions(quotation) {
        return `
            <div class="dropdown">
                <button class="btn btn-sm btn-light" data-bs-toggle="dropdown">
                    <i class="ri-more-2-fill"></i>
                </button>
                <ul class="dropdown-menu">
                    <li>
                        <a class="dropdown-item" href="/quotations/${quotation.id}/">
                            <i class="ri-eye-line"></i> View Details
                        </a>
                    </li>
                    ${quotation.status === 'draft' ? `
                    <li>
                        <a class="dropdown-item" href="#" 
                           onclick="editQuotation(${quotation.id})">
                            <i class="ri-pencil-line"></i> Edit
                        </a>
                    </li>
                    ` : ''}
                    <li>
                        <a class="dropdown-item" href="#" 
                           onclick="sendQuotation(${quotation.id})">
                            <i class="ri-mail-line"></i> Send to Customer
                        </a>
                    </li>
                    <li>
                        <a class="dropdown-item" href="#" 
                           onclick="downloadPDF(${quotation.id})">
                            <i class="ri-download-line"></i> Download PDF
                        </a>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                        <a class="dropdown-item text-danger" href="#" 
                           onclick="deleteQuotation(${quotation.id})">
                            <i class="ri-delete-bin-line"></i> Delete
                        </a>
                    </li>
                </ul>
            </div>
        `;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    async refreshQuotations() {
        try {
            const response = await fetch('/api/quotations/');
            const data = await response.json();
            this.updateQuotationsTable(data);
        } catch (error) {
            this.showNotification('Error refreshing quotations', 'error');
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

// Initialize Quotation Manager
document.addEventListener('DOMContentLoaded', () => {
    window.quotationManager = new QuotationManager();
}); 