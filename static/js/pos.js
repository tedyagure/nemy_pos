class POSSystem {
    constructor() {
        this.cart = [];
        this.customer = null;
        this.paymentMethod = 'cash';
        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

        // Initialize modals
        this.paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
        this.customerModal = new bootstrap.Modal(document.getElementById('customerModal'));
    }

    setupEventListeners() {
        // Category filtering
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', () => this.filterProducts(btn.dataset.category));
        });

        // Product search
        document.getElementById('productSearch')?.addEventListener('input', (e) => {
            this.searchProducts(e.target.value);
        });

        // Product selection
        document.querySelectorAll('.product-card').forEach(card => {
            card.addEventListener('click', () => this.addToCart(card.dataset.id));
        });

        // Cart actions
        document.getElementById('clearCart')?.addEventListener('click', () => this.clearCart());
        document.getElementById('holdSale')?.addEventListener('click', () => this.holdSale());
        document.getElementById('checkoutBtn')?.addEventListener('click', () => this.initiateCheckout());

        // Discount input
        document.getElementById('discountInput')?.addEventListener('input', (e) => {
            this.updateDiscount(e.target.value);
        });

        // Payment method selection
        document.querySelectorAll('.payment-method-btn').forEach(btn => {
            btn.addEventListener('click', () => this.selectPaymentMethod(btn.dataset.method));
        });

        // Complete payment
        document.getElementById('completePayment')?.addEventListener('click', () => this.processPayment());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }

    async addToCart(productId) {
        try {
            const response = await fetch(`/api/products/${productId}/`);
            const product = await response.json();
            
            const existingItem = this.cart.find(item => item.id === product.id);
            
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                this.cart.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    quantity: 1
                });
            }
            
            this.updateCartDisplay();
        } catch (error) {
            this.showNotification('Error adding product to cart', 'error');
        }
    }

    updateCartDisplay() {
        const cartContainer = document.getElementById('cartItems');
        if (!cartContainer) return;

        cartContainer.innerHTML = this.cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <h6>${item.name}</h6>
                    <p class="text-muted">₦${item.price} × ${item.quantity}</p>
                </div>
                <div class="cart-item-quantity">
                    <button class="btn btn-sm btn-light quantity-btn" 
                            onclick="pos.updateQuantity(${item.id}, ${item.quantity - 1})">
                        <i class="ri-subtract-line"></i>
                    </button>
                    <span>${item.quantity}</span>
                    <button class="btn btn-sm btn-light quantity-btn"
                            onclick="pos.updateQuantity(${item.id}, ${item.quantity + 1})">
                        <i class="ri-add-line"></i>
                    </button>
                </div>
                <button class="btn btn-sm btn-light ms-2" 
                        onclick="pos.removeFromCart(${item.id})">
                    <i class="ri-delete-bin-line"></i>
                </button>
            </div>
        `).join('');

        this.updateTotals();
    }

    updateTotals() {
        const subtotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const discount = parseFloat(document.getElementById('discountInput')?.value || 0);
        const tax = subtotal * 0.075; // 7.5% VAT
        const total = (subtotal + tax) * (1 - discount / 100);

        document.querySelector('.subtotal').textContent = `₦${subtotal.toFixed(2)}`;
        document.querySelector('.tax').textContent = `₦${tax.toFixed(2)}`;
        document.querySelector('.total-amount').textContent = `₦${total.toFixed(2)}`;
        document.getElementById('checkoutBtn').textContent = `Checkout (₦${total.toFixed(2)})`;
    }

    async initiateCheckout() {
        if (this.cart.length === 0) {
            this.showNotification('Cart is empty', 'warning');
            return;
        }

        // Show payment modal
        this.paymentModal.show();
        this.updatePaymentSummary();
    }

    async processPayment() {
        try {
            const paymentData = {
                items: this.cart,
                customer: this.customer,
                payment_method: this.paymentMethod,
                discount: parseFloat(document.getElementById('discountInput').value || 0),
                total: this.calculateTotal()
            };

            const response = await fetch('/api/sales/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(paymentData)
            });

            if (!response.ok) throw new Error('Payment failed');

            const result = await response.json();
            this.showNotification('Payment successful', 'success');
            this.printReceipt(result.sale_id);
            this.clearCart();
            this.paymentModal.hide();

        } catch (error) {
            this.showNotification('Payment failed: ' + error.message, 'error');
        }
    }

    // Utility functions
    showNotification(message, type = 'info') {
        // Implementation depends on your notification system
        console.log(`${type}: ${message}`);
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    handleKeyboardShortcuts(e) {
        // Ctrl + / for search
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            document.getElementById('productSearch')?.focus();
        }
        // F2 for checkout
        if (e.key === 'F2') {
            e.preventDefault();
            this.initiateCheckout();
        }
        // Esc to clear search
        if (e.key === 'Escape') {
            document.getElementById('productSearch').value = '';
            this.searchProducts('');
        }
    }
}

// Initialize POS System
document.addEventListener('DOMContentLoaded', () => {
    window.pos = new POSSystem();
}); 