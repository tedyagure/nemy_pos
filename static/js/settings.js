class SettingsManager {
    constructor() {
        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

        // Initialize modals
        this.paymentMethodModal = new bootstrap.Modal(document.getElementById('paymentMethodModal'));
        this.taxRateModal = new bootstrap.Modal(document.getElementById('taxRateModal'));
        this.userModal = new bootstrap.Modal(document.getElementById('userModal'));
    }

    setupEventListeners() {
        // Business Profile Form
        document.getElementById('businessForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveBusinessProfile();
        });

        // Logo Upload
        document.getElementById('logoInput')?.addEventListener('change', (e) => {
            this.handleLogoUpload(e);
        });

        // Invoice Settings Form
        document.getElementById('invoiceForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveInvoiceSettings();
        });

        // Payment Method Toggles
        document.querySelectorAll('.payment-method-item .form-check-input').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this.togglePaymentMethod(e.target.id.replace('payment', ''), e.target.checked);
            });
        });
    }

    async saveBusinessProfile() {
        const form = document.getElementById('businessForm');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/settings/business/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to save business profile');

            this.showNotification('Business profile updated successfully', 'success');
        } catch (error) {
            this.showNotification('Error saving business profile: ' + error.message, 'error');
        }
    }

    handleLogoUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('logoPreview').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    async saveInvoiceSettings() {
        const form = document.getElementById('invoiceForm');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/settings/invoice/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to save invoice settings');

            this.showNotification('Invoice settings updated successfully', 'success');
        } catch (error) {
            this.showNotification('Error saving invoice settings: ' + error.message, 'error');
        }
    }

    async togglePaymentMethod(methodId, enabled) {
        try {
            const response = await fetch(`/api/settings/payment-methods/${methodId}/toggle/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ enabled })
            });

            if (!response.ok) throw new Error('Failed to update payment method');

            this.showNotification(
                `Payment method ${enabled ? 'enabled' : 'disabled'} successfully`, 
                'success'
            );
        } catch (error) {
            this.showNotification('Error updating payment method: ' + error.message, 'error');
        }
    }

    // Payment Method Management
    async addPaymentMethod() {
        document.getElementById('paymentMethodForm').reset();
        document.getElementById('paymentMethodModalTitle').textContent = 'Add Payment Method';
        this.paymentMethodModal.show();
    }

    async configurePayment(methodId) {
        try {
            const response = await fetch(`/api/settings/payment-methods/${methodId}/`);
            const method = await response.json();
            
            // Populate form
            const form = document.getElementById('paymentMethodForm');
            form.querySelector('[name="name"]').value = method.name;
            form.querySelector('[name="provider"]').value = method.provider;
            form.querySelector('[name="api_key"]').value = method.api_key;
            form.querySelector('[name="secret_key"]').value = method.secret_key;
            
            document.getElementById('paymentMethodModalTitle').textContent = 'Configure Payment Method';
            form.dataset.methodId = methodId;
            this.paymentMethodModal.show();
        } catch (error) {
            this.showNotification('Error loading payment method details', 'error');
        }
    }

    // Tax Rate Management
    async addTaxRate() {
        document.getElementById('taxRateForm').reset();
        document.getElementById('taxRateModalTitle').textContent = 'Add Tax Rate';
        this.taxRateModal.show();
    }

    async editTaxRate(taxId) {
        try {
            const response = await fetch(`/api/settings/tax-rates/${taxId}/`);
            const tax = await response.json();
            
            // Populate form
            const form = document.getElementById('taxRateForm');
            form.querySelector('[name="name"]').value = tax.name;
            form.querySelector('[name="rate"]').value = tax.rate;
            form.querySelector('[name="description"]').value = tax.description;
            
            document.getElementById('taxRateModalTitle').textContent = 'Edit Tax Rate';
            form.dataset.taxId = taxId;
            this.taxRateModal.show();
        } catch (error) {
            this.showNotification('Error loading tax rate details', 'error');
        }
    }

    async deleteTaxRate(taxId) {
        if (!confirm('Are you sure you want to delete this tax rate?')) return;

        try {
            const response = await fetch(`/api/settings/tax-rates/${taxId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Failed to delete tax rate');

            this.showNotification('Tax rate deleted successfully', 'success');
            this.refreshTaxRates();
        } catch (error) {
            this.showNotification('Error deleting tax rate: ' + error.message, 'error');
        }
    }

    // User Management
    async addUser() {
        document.getElementById('userForm').reset();
        document.getElementById('userModalTitle').textContent = 'Add User';
        this.userModal.show();
    }

    async editUser(userId) {
        try {
            const response = await fetch(`/api/settings/users/${userId}/`);
            const user = await response.json();
            
            // Populate form
            const form = document.getElementById('userForm');
            form.querySelector('[name="name"]').value = user.name;
            form.querySelector('[name="email"]').value = user.email;
            form.querySelector('[name="role"]').value = user.role;
            
            document.getElementById('userModalTitle').textContent = 'Edit User';
            form.dataset.userId = userId;
            this.userModal.show();
        } catch (error) {
            this.showNotification('Error loading user details', 'error');
        }
    }

    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user?')) return;

        try {
            const response = await fetch(`/api/settings/users/${userId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Failed to delete user');

            this.showNotification('User deleted successfully', 'success');
            this.refreshUsers();
        } catch (error) {
            this.showNotification('Error deleting user: ' + error.message, 'error');
        }
    }

    // Utility Methods
    showNotification(message, type = 'info') {
        // Implementation depends on your notification system
        console.log(`${type}: ${message}`);
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    async refreshTaxRates() {
        try {
            const response = await fetch('/api/settings/tax-rates/');
            const data = await response.json();
            // Update tax rates list in the DOM
            this.updateTaxRatesList(data);
        } catch (error) {
            this.showNotification('Error refreshing tax rates', 'error');
        }
    }

    async refreshUsers() {
        try {
            const response = await fetch('/api/settings/users/');
            const data = await response.json();
            // Update users list in the DOM
            this.updateUsersList(data);
        } catch (error) {
            this.showNotification('Error refreshing users', 'error');
        }
    }
}

// Initialize Settings Manager
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
}); 