class InventoryManager {
    constructor() {
        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }

    setupEventListeners() {
        // Search functionality
        document.getElementById('searchProduct')?.addEventListener('input', (e) => {
            this.filterProducts(e.target.value);
        });

        // Category filter
        document.getElementById('categoryFilter')?.addEventListener('change', (e) => {
            this.filterByCategory(e.target.value);
        });

        // Stock filter
        document.getElementById('stockFilter')?.addEventListener('change', (e) => {
            this.filterByStock(e.target.value);
        });

        // Image upload preview
        document.querySelector('.image-upload-wrapper input[type="file"]')?.addEventListener('change', (e) => {
            this.handleImageUpload(e);
        });
    }

    async filterProducts(query) {
        try {
            const response = await fetch(`/api/products/search/?q=${query}`);
            const data = await response.json();
            this.updateProductTable(data);
        } catch (error) {
            console.error('Error filtering products:', error);
        }
    }

    async filterByCategory(categoryId) {
        try {
            const response = await fetch(`/api/products/filter/?category=${categoryId}`);
            const data = await response.json();
            this.updateProductTable(data);
        } catch (error) {
            console.error('Error filtering by category:', error);
        }
    }

    async filterByStock(status) {
        try {
            const response = await fetch(`/api/products/filter/?stock_status=${status}`);
            const data = await response.json();
            this.updateProductTable(data);
        } catch (error) {
            console.error('Error filtering by stock:', error);
        }
    }

    updateProductTable(products) {
        const tbody = document.querySelector('.inventory-table tbody');
        if (!tbody) return;

        tbody.innerHTML = products.map(product => `
            <tr>
                <td>
                    <div class="product-cell">
                        <img src="${product.image || 'static/img/default-product.png'}" 
                             alt="${product.name}" class="product-img">
                        <div>
                            <h6 class="product-name">${product.name}</h6>
                            <span class="product-sku">SKU: ${product.sku}</span>
                        </div>
                    </div>
                </td>
                <td>${product.category}</td>
                <td>
                    <div class="stock-cell">
                        <span class="stock-number">${product.stock}</span>
                        ${product.is_low_stock ? '<span class="badge bg-warning">Low Stock</span>' : ''}
                    </div>
                </td>
                <td>₦${product.price}</td>
                <td>
                    <span class="badge bg-${product.status_color}">${product.status}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-light" onclick="editProduct(${product.id})">
                            <i class="ri-pencil-line"></i>
                        </button>
                        <button class="btn btn-sm btn-light" onclick="adjustStock(${product.id})">
                            <i class="ri-stack-line"></i>
                        </button>
                        <button class="btn btn-sm btn-light text-danger" onclick="deleteProduct(${product.id})">
                            <i class="ri-delete-bin-line"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.querySelector('.modal-product-image');
            if (preview) {
                preview.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);
    }

    // Product CRUD operations
    async addProduct(formData) {
        try {
            const response = await fetch('/api/products/', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Failed to add product');
            
            const data = await response.json();
            this.showNotification('Product added successfully', 'success');
            return data;
        } catch (error) {
            this.showNotification(error.message, 'error');
            throw error;
        }
    }

    // More methods for edit, delete, and stock adjustment...
}

// Initialize Inventory Manager
document.addEventListener('DOMContentLoaded', () => {
    window.inventoryManager = new InventoryManager();
}); 