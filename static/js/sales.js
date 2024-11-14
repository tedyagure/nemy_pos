class SalesHistory {
    constructor() {
        this.initializeComponents();
        this.setupEventListeners();
        this.setupDateRangePicker();
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

        // Initialize modals
        this.exportModal = new bootstrap.Modal(document.getElementById('exportModal'));
        this.refundModal = new bootstrap.Modal(document.getElementById('refundModal'));
    }

    setupEventListeners() {
        // Date range selector
        document.getElementById('dateRange')?.addEventListener('change', (e) => {
            this.handleDateRangeChange(e.target.value);
        });

        // Filters
        document.getElementById('paymentMethod')?.addEventListener('change', () => {
            this.applyFilters();
        });

        document.getElementById('saleStatus')?.addEventListener('change', () => {
            this.applyFilters();
        });

        // Search
        document.getElementById('searchSales')?.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });
    }

    setupDateRangePicker() {
        // Initialize date range picker for export
        const exportDateRange = document.getElementById('exportDateRange');
        if (exportDateRange) {
            new DateRangePicker(exportDateRange, {
                ranges: {
                    'Today': [moment(), moment()],
                    'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                    'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                    'This Month': [moment().startOf('month'), moment().endOf('month')]
                }
            });
        }
    }

    async handleDateRangeChange(range) {
        let startDate, endDate;

        switch (range) {
            case 'today':
                startDate = moment().startOf('day');
                endDate = moment().endOf('day');
                break;
            case 'yesterday':
                startDate = moment().subtract(1, 'days').startOf('day');
                endDate = moment().subtract(1, 'days').endOf('day');
                break;
            case 'last7days':
                startDate = moment().subtract(6, 'days').startOf('day');
                endDate = moment().endOf('day');
                break;
            case 'thisMonth':
                startDate = moment().startOf('month');
                endDate = moment().endOf('month');
                break;
            case 'custom':
                // Show date range picker modal
                return;
        }

        await this.fetchSales(startDate, endDate);
    }

    async fetchSales(startDate, endDate) {
        try {
            const response = await fetch(`/api/sales/?start_date=${startDate.format('YYYY-MM-DD')}&end_date=${endDate.format('YYYY-MM-DD')}`);
            const data = await response.json();
            this.updateSalesTable(data);
        } catch (error) {
            this.showNotification('Error fetching sales data', 'error');
        }
    }

    updateSalesTable(sales) {
        const tbody = document.querySelector('table tbody');
        if (!tbody) return;

        tbody.innerHTML = sales.map(sale => `
            <tr>
                <td>
                    <a href="/sales/${sale.id}/" class="sale-id">#${sale.id}</a>
                </td>
                <td>
                    <div class="sale-date">
                        ${moment(sale.created_at).format('MMM D, YYYY')}
                        <small class="text-muted">
                            ${moment(sale.created_at).format('HH:mm')}
                        </small>
                    </div>
                </td>
                <td>
                    ${sale.customer ? `
                        <div class="customer-info">
                            <span>${sale.customer.name}</span>
                            <small class="text-muted">${sale.customer.phone}</small>
                        </div>
                    ` : '<span class="text-muted">Walk-in Customer</span>'}
                </td>
                <td>${sale.items_count} items</td>
                <td>
                    <span class="payment-method">
                        <i class="ri-${sale.payment_method_icon}-line"></i>
                        ${sale.payment_method}
                    </span>
                </td>
                <td>
                    <span class="sale-amount">₦${sale.total}</span>
                </td>
                <td>
                    <span class="badge bg-${sale.status_color}">
                        ${sale.status}
                    </span>
                </td>
                <td>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-light" data-bs-toggle="dropdown">
                            <i class="ri-more-2-fill"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li>
                                <a class="dropdown-item" href="/sales/${sale.id}/">
                                    <i class="ri-eye-line"></i> View Details
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item" href="#" 
                                   onclick="salesHistory.printReceipt('${sale.id}')">
                                    <i class="ri-printer-line"></i> Print Receipt
                                </a>
                            </li>
                            ${sale.status === 'completed' ? `
                                <li>
                                    <a class="dropdown-item text-danger" href="#"
                                       onclick="salesHistory.initializeRefund('${sale.id}')">
                                        <i class="ri-refund-line"></i> Refund
                                    </a>
                                </li>
                            ` : ''}
                        </ul>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    async handleSearch(query) {
        if (query.length < 2) return;

        try {
            const response = await fetch(`/api/sales/search/?q=${query}`);
            const data = await response.json();
            this.updateSalesTable(data);
        } catch (error) {
            this.showNotification('Error searching sales', 'error');
        }
    }

    async exportSales() {
        const format = document.getElementById('exportFormat').value;
        const dateRange = document.getElementById('exportDateRange').value;

        try {
            const response = await fetch('/api/sales/export/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    format,
                    date_range: dateRange
                })
            });

            if (!response.ok) throw new Error('Export failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sales_export_${moment().format('YYYY-MM-DD')}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.exportModal.hide();
            this.showNotification('Export completed successfully', 'success');

        } catch (error) {
            this.showNotification('Export failed: ' + error.message, 'error');
        }
    }

    async initializeRefund(saleId) {
        try {
            const response = await fetch(`/api/sales/${saleId}/`);
            const sale = await response.json();
            
            // Populate refund modal with sale details
            document.getElementById('refundSaleId').textContent = sale.id;
            document.getElementById('refundAmount').value = sale.total;
            
            this.refundModal.show();
        } catch (error) {
            this.showNotification('Error loading sale details', 'error');
        }
    }

    async processRefund(saleId) {
        const amount = document.getElementById('refundAmount').value;
        const reason = document.getElementById('refundReason').value;

        try {
            const response = await fetch(`/api/sales/${saleId}/refund/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ amount, reason })
            });

            if (!response.ok) throw new Error('Refund failed');

            this.refundModal.hide();
            this.showNotification('Refund processed successfully', 'success');
            this.fetchSales(); // Refresh the table

        } catch (error) {
            this.showNotification('Refund failed: ' + error.message, 'error');
        }
    }

    async printReceipt(saleId) {
        try {
            const response = await fetch(`/api/sales/${saleId}/receipt/`);
            const data = await response.blob();
            
            const url = window.URL.createObjectURL(data);
            const printWindow = window.open(url);
            printWindow.onload = function() {
                printWindow.print();
                window.URL.revokeObjectURL(url);
            };
        } catch (error) {
            this.showNotification('Error printing receipt', 'error');
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

// Initialize Sales History
document.addEventListener('DOMContentLoaded', () => {
    window.salesHistory = new SalesHistory();
}); 