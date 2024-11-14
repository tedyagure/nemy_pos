class CustomerManager {
    constructor() {
        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

        // Initialize modals
        this.customerModal = new bootstrap.Modal(document.getElementById('customerModal'));
        this.messageModal = new bootstrap.Modal(document.getElementById('messageModal'));
    }

    setupEventListeners() {
        // Search functionality
        document.getElementById('customerSearch')?.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Status filter
        document.getElementById('customerStatus')?.addEventListener('change', (e) => {
            this.filterByStatus(e.target.value);
        });

        // Sort options
        document.getElementById('customerSort')?.addEventListener('change', (e) => {
            this.sortCustomers(e.target.value);
        });

        // Form submission
        document.getElementById('customerForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCustomer();
        });
    }

    async handleSearch(query) {
        if (query.length < 2) return;

        try {
            const response = await fetch(`/api/customers/search/?q=${query}`);
            const data = await response.json();
            this.updateCustomersTable(data);
        } catch (error) {
            this.showNotification('Error searching customers', 'error');
        }
    }

    async filterByStatus(status) {
        try {
            const response = await fetch(`/api/customers/filter/?status=${status}`);
            const data = await response.json();
            this.updateCustomersTable(data);
        } catch (error) {
            this.showNotification('Error filtering customers', 'error');
        }
    }

    async sortCustomers(sortBy) {
        try {
            const response = await fetch(`/api/customers/sort/?sort=${sortBy}`);
            const data = await response.json();
            this.updateCustomersTable(data);
        } catch (error) {
            this.showNotification('Error sorting customers', 'error');
        }
    }

    updateCustomersTable(customers) {
        const tbody = document.querySelector('table tbody');
        if (!tbody) return;

        tbody.innerHTML = customers.map(customer => `
            <tr>
                <td>
                    <div class="customer-info">
                        <div class="customer-avatar">
                            ${customer.avatar ? 
                                `<img src="${customer.avatar}" alt="${customer.name}">` :
                                `<div class="avatar-placeholder">${customer.name[0].toUpperCase()}</div>`
                            }
                        </div>
                        <div>
                            <h6 class="customer-name">${customer.name}</h6>
                            <span class="customer-id">#${customer.id}</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="contact-info">
                        <div><i class="ri-phone-line"></i> ${customer.phone}</div>
                        ${customer.email ? 
                            `<div><i class="ri-mail-line"></i> ${customer.email}</div>` : 
                            ''
                        }
                    </div>
                </td>
                <td>
                    <div class="sales-info">
                        <div class="total-amount">₦${customer.total_sales}</div>
                        <small class="text-muted">${customer.orders_count} orders</small>
                    </div>
                </td>
                <td>
                    ${customer.last_purchase ? 
                        `<div class="last-purchase">
                            ${moment(customer.last_purchase).format('MMM D, YYYY')}
                            <small class="text-muted">
                                ${moment(customer.last_purchase).format('HH:mm')}
                            </small>
                        </div>` :
                        '<span class="text-muted">No purchases yet</span>'
                    }
                </td>
                <td>
                    <span class="badge bg-${customer.status_color}">
                        ${customer.status}
                    </span>
                </td>
                <td>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-light" data-bs-toggle="dropdown">
                            <i class="ri-more-2-fill"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li>
                                <a class="dropdown-item" href="/customers/${customer.id}/">
                                    <i class="ri-eye-line"></i> View Details
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item" href="#" 
                                   onclick="customerManager.editCustomer('${customer.id}')">
                                    <i class="ri-pencil-line"></i> Edit
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item" href="#"
                                   onclick="customerManager.sendMessage('${customer.id}')">
                                    <i class="ri-message-2-line"></i> Send Message
                                </a>
                            </li>
                            <li><hr class="dropdown-divider"></li>
                            <li>
                                <a class="dropdown-item text-danger" href="#"
                                   onclick="customerManager.deleteCustomer('${customer.id}')">
                                    <i class="ri-delete-bin-line"></i> Delete
                                </a>
                            </li>
                        </ul>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    async editCustomer(customerId) {
        try {
            const response = await fetch(`/api/customers/${customerId}/`);
            const customer = await response.json();
            
            // Populate form
            const form = document.getElementById('customerForm');
            form.querySelector('[name="name"]').value = customer.name;
            form.querySelector('[name="phone"]').value = customer.phone;
            form.querySelector('[name="email"]').value = customer.email || '';
            form.querySelector('[name="address"]').value = customer.address || '';
            form.querySelector('[name="notes"]').value = customer.notes || '';
            
            // Update modal title and show
            document.getElementById('modalTitle').textContent = 'Edit Customer';
            form.dataset.customerId = customerId;
            this.customerModal.show();
        } catch (error) {
            this.showNotification('Error loading customer details', 'error');
        }
    }

    async saveCustomer() {
        const form = document.getElementById('customerForm');
        const formData = new FormData(form);
        const customerId = form.dataset.customerId;

        try {
            const response = await fetch(customerId ? 
                `/api/customers/${customerId}/` : 
                '/api/customers/', {
                method: customerId ? 'PUT' : 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to save customer');

            this.customerModal.hide();
            this.showNotification(
                `Customer ${customerId ? 'updated' : 'added'} successfully`, 
                'success'
            );
            this.refreshCustomers();

        } catch (error) {
            this.showNotification('Error saving customer: ' + error.message, 'error');
        }
    }

    async deleteCustomer(customerId) {
        if (!confirm('Are you sure you want to delete this customer?')) return;

        try {
            const response = await fetch(`/api/customers/${customerId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Failed to delete customer');

            this.showNotification('Customer deleted successfully', 'success');
            this.refreshCustomers();

        } catch (error) {
            this.showNotification('Error deleting customer: ' + error.message, 'error');
        }
    }

    async sendMessage(customerId) {
        try {
            const response = await fetch(`/api/customers/${customerId}/`);
            const customer = await response.json();
            
            // Populate message form
            const form = document.getElementById('messageForm');
            form.dataset.customerId = customerId;
            
            this.messageModal.show();
        } catch (error) {
            this.showNotification('Error loading customer details', 'error');
        }
    }

    async sendCustomerMessage() {
        const form = document.getElementById('messageForm');
        const formData = new FormData(form);
        const customerId = form.dataset.customerId;

        try {
            const response = await fetch(`/api/customers/${customerId}/message/`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to send message');

            this.messageModal.hide();
            this.showNotification('Message sent successfully', 'success');

        } catch (error) {
            this.showNotification('Error sending message: ' + error.message, 'error');
        }
    }

    async refreshCustomers() {
        try {
            const response = await fetch('/api/customers/');
            const data = await response.json();
            this.updateCustomersTable(data);
        } catch (error) {
            this.showNotification('Error refreshing customers', 'error');
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

// Initialize Customer Manager
document.addEventListener('DOMContentLoaded', () => {
    window.customerManager = new CustomerManager();
}); 