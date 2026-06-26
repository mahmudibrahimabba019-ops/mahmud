// ============================================
// VIBRANT SPICES - MAIN APPLICATION
// ============================================

// ============ CART MANAGEMENT ============
class Cart {
    constructor() {
        this.items = this.loadCart();
    }

    loadCart() {
        // prefer unified 'cart' key, fallback to legacy keys
        const raw = localStorage.getItem('cart') || localStorage.getItem('halari_cart') || localStorage.getItem('spices_cart');
        if (!raw) return [];
        try {
            const parsed = JSON.parse(raw);
            // support both array and object formats
            if (Array.isArray(parsed)) return parsed;
            if (parsed.items && Array.isArray(parsed.items)) return parsed.items;
            return [];
        } catch (e) { return []; }
    }

    saveCart() {
        // Save in unified cart object format
        const cartObj = {
            items: this.items,
            subtotal: this.getTotal(),
            delivery_fee: 3000,
            total: this.getTotal() + 3000
        };
        localStorage.setItem('cart', JSON.stringify(cartObj));
        // also keep legacy keys in sync for compatibility
        localStorage.setItem('halari_cart', JSON.stringify(cartObj));
        localStorage.setItem('spices_cart', JSON.stringify(cartObj));
        console.log('Cart saved', cartObj);
        this.updateCartCount();
    }

    addItem(product, quantity = 1) {
        const existingItem = this.items.find(item => item.product_id === product.id && item.variant === (product.variant||''));
        if (existingItem) {
            existingItem.quantity += quantity;
            existingItem.subtotal = existingItem.quantity * existingItem.price;
        } else {
            this.items.push({
                product_id: product.id,
                product_name: product.name,
                price: Number(product.price || 0),
                quantity: Number(quantity || 1),
                subtotal: Number((product.price || 0) * quantity),
                image: product.image || null,
                variant: product.variant || ''
            });
        }
        this.saveCart();
    }

    removeItem(productId) {
        this.items = this.items.filter(item => item.product_id !== productId);
        this.saveCart();
    }

    updateQuantity(productId, quantity) {
        console.log('[cart.updateQuantity] Looking for productId:', productId);
        console.log('[cart.updateQuantity] Current items:', this.items);
        const item = this.items.find(item => item.product_id === productId);
        console.log('[cart.updateQuantity] Found item:', item);
        if (item) {
            if (quantity <= 0) {
                this.removeItem(productId);
            } else {
                item.quantity = quantity;
                item.subtotal = item.quantity * item.price;
                this.saveCart();
            }
        } else {
            console.log('[cart.updateQuantity] Item not found with product_id, trying id field');
            const itemById = this.items.find(item => item.id === productId);
            if (itemById) {
                if (quantity <= 0) {
                    this.removeItem(productId);
                } else {
                    itemById.quantity = quantity;
                    itemById.subtotal = itemById.quantity * itemById.price;
                    this.saveCart();
                }
            }
        }
    }

    getTotal() {
        return this.items.reduce((total, item) => total + (Number(item.price || 0) * Number(item.quantity || 0)), 0);
    }

    getCount() {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    }

    clear() {
        this.items = [];
        this.saveCart();
    }

    updateCartCount() {
        const count = this.getCount();
        document.querySelectorAll('#cart-count').forEach(el => {
            el.textContent = count;
        });
    }
}

// Initialize cart
const cart = new Cart();
const API_BASE = 'http://127.0.0.1:8001';

function productImageUrl(filename){
    if(!filename) return (window.location.protocol === 'file:') ? './halari.jpg' : API_BASE + '/images/' + encodeURIComponent('halari.jpg');
    if(filename.startsWith('http://')||filename.startsWith('https://')) return filename;
    if(window.location.protocol === 'file:') return './' + filename;
    return API_BASE + '/images/' + encodeURIComponent(filename);
}

// ============ PRODUCT RENDERING ============
function renderProducts(products = ALL_PRODUCTS) {
    const grid = document.getElementById('products-grid');
    if (!grid) return;

    grid.innerHTML = products.map(product => `
        <div class="product-card" data-category="${product.category}">
            <div class="product-image">
                <a href="product-detail.html?id=${product.id}"><img src="${productImageUrl(product.image)}" alt="${product.name}" loading="lazy"></a>
            </div>
            <div class="product-info">
                <div class="product-category">${product.category}</div>
                <h3 class="product-name"><a href="product-detail.html?id=${product.id}">${product.name}</a></h3>
                <div class="product-footer">
                    <a class="view-details-btn" href="product-detail.html?id=${product.id}">View Details</a>
                </div>
            </div>
        </div>
    `).join('');
}

// Featured products removed

function addToCart(productId) {
    // Normalize id comparison to handle string/number mismatches
    const pid = (typeof productId === 'string' && !isNaN(productId)) ? Number(productId) : productId;
    let product = null;
    try {
        product = ALL_PRODUCTS.find(p => String(p.id) === String(pid));
    } catch (e) { product = null; }

    // Fallbacks: try helper, then PRODUCTS array
    if (!product && typeof getProductById === 'function') {
        product = getProductById(pid);
    }
    if (!product && typeof PRODUCTS !== 'undefined') {
        product = (Array.isArray(PRODUCTS) && PRODUCTS.find(p => String(p.id) === String(pid))) || null;
    }

    const name = product && (product.name || product.product_name || product.title) ? (product.name || product.product_name || product.title) : 'Item';
    const price = product ? Number(product.price || 0) : 0;
    const prodObj = { id: (product && product.id) || pid, product_id: (product && product.id) || pid, name: name, product_name: name, price: price, image: product ? product.image : null };

    cart.addItem(prodObj);
    showNotification(`${name} added to cart!`);
}

function showNotification(message) {
    // Toast notification
    let toast = document.getElementById('site-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'site-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.remove('show');
    void toast.offsetWidth;
    toast.classList.add('show');
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        cartCount.classList.add('pulse');
        setTimeout(() => cartCount.classList.remove('pulse'), 900);
    }
    clearTimeout(window._toastTimeout);
    window._toastTimeout = setTimeout(() => {
        if (toast) toast.classList.remove('show');
    }, 3000);
}

// ============ FILTERING ============
function setupFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter products
            const filter = btn.dataset.filter;
            const products = filter === 'all' 
                ? ALL_PRODUCTS 
                : ALL_PRODUCTS.filter(p => p.category === filter);

            renderProducts(products);
        });
    });
}

// ============ CART PAGE ============
function renderCart() {
    const cartContent = document.getElementById('cart-content');
    const emptyMsg = document.getElementById('empty-cart-msg');
    const cartItems = document.getElementById('cart-items');

    if (!cartItems) return;

    if (cart.items.length === 0) {
        if (emptyMsg) emptyMsg.style.display = 'block';
        if (cartContent) cartContent.style.display = 'none';
        return;
    }

    if (emptyMsg) emptyMsg.style.display = 'none';
    if (cartContent) cartContent.style.display = 'grid';

    cartItems.innerHTML = cart.items.map(item => {
        const name = item.product_name || item.name || item.product || 'Item';
        const qty = Number(item.quantity || 0);
        const pid = item.product_id || item.id || item.product;
        const price = Number(item.price || 0);
        return `
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-name">${name}</div>
                <div class="cart-item-price">₦${price.toLocaleString()} each</div>
            </div>
            <div class="cart-item-quantity">
                <button class="quantity-btn" onclick="updateQuantity(${pid}, ${Math.max(0, qty - 1)})">−</button>
                <span class="quantity-number">${qty}</span>
                <button class="quantity-btn" onclick="updateQuantity(${pid}, ${qty + 1})">+</button>
                <button class="remove-btn" onclick="removeFromCart(${pid})">Remove</button>
            </div>
        </div>
    `}).join('');

    updateCartSummary();
}

function updateQuantity(productId, newQuantity) {
    console.log('[updateQuantity] Called with productId:', productId, 'newQuantity:', newQuantity);
    console.log('[updateQuantity] Current cart items:', cart.items);
    if (newQuantity <= 0) {
        removeFromCart(productId);
    } else {
        cart.updateQuantity(productId, newQuantity);
        renderCart();
    }
}

function removeFromCart(productId) {
    cart.removeItem(productId);
    renderCart();
}

function updateCartSummary() {
    const subtotal = cart.getTotal();
    const delivery = 3000;
    const total = subtotal + delivery;

    const subtotalEl = document.getElementById('subtotal');
    const totalEl = document.getElementById('total');
    const deliveryEl = document.getElementById('deliveryFee');
    if (subtotalEl) subtotalEl.textContent = subtotal.toLocaleString();
    if (deliveryEl) deliveryEl.textContent = `₦${delivery.toLocaleString()}`;
    if (totalEl) totalEl.textContent = total.toLocaleString();
}


function clearCart() {
    if (confirm('Are you sure you want to clear your cart?')) {
        cart.clear();
        renderCart();
    }
}

function generateQRCode() {
    const qrCodeDiv = document.getElementById('qr-code');
    if (!qrCodeDiv) return;

    // Clear previous QR code
    qrCodeDiv.innerHTML = '';

    // Instagram DM URL
    const instagramUsername = 'halari.seasonings';
    const dmUrl = `https://www.instagram.com/${instagramUsername}/`;

    // Generate QR code using QRCode library
    try {
        new QRCode(qrCodeDiv, {
            text: dmUrl,
            width: 200,
            height: 200,
            colorDark: '#C9A84D',
            colorLight: '#071014'
        });
    } catch (e) {
        console.log('QR code generation error:', e);
    }
}

// ============ INITIALIZATION ============
document.addEventListener('DOMContentLoaded', function() {
    // Update cart count on page load
    cart.updateCartCount();

    // Render products if we're on the catalog page
    if (document.getElementById('products-grid')) {
        setupFilters();

        function applyActiveFilter() {
            const activeBtn = document.querySelector('.filter-btn.active');
            const filter = (activeBtn && activeBtn.dataset) ? activeBtn.dataset.filter : 'spices';
            const products = (filter === 'all') ? ALL_PRODUCTS : ALL_PRODUCTS.filter(p => p.category === filter);
            renderProducts(products);
        }

        // If products already loaded, render immediately; otherwise wait for the productsLoaded event
        if (Array.isArray(ALL_PRODUCTS) && ALL_PRODUCTS.length) {
            applyActiveFilter();
        } else {
            window.addEventListener('productsLoaded', applyActiveFilter);
        }
    }

    // Featured products and bestsellers removed from homepage

    // Initialize testimonial slider if on home page
    if (document.querySelector('.testimonial-card')) {
        showTestimonial(currentSlide);
    }

    // Render cart if we're on the cart page
    if (document.getElementById('cart-items')) {
        renderCart();
    }

    // Setup navigation active state
    updateActiveNav();
});

function updateActiveNav() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        link.classList.remove('active');
        
        if (currentPage === '' && href === 'index.html') {
            link.classList.add('active');
        } else if (currentPage === href) {
            link.classList.add('active');
        }
    });
}

// ============ BEST SELLERS GRID ============
function renderBestSellers() {
    const bestsellersGrid = document.getElementById('bestsellers-grid');
    if (!bestsellersGrid) return;
    
    // Select best-selling products (mix of high-value items and popular ones)
    const bestsellerIds = [1, 5, 8, 15, 22, 28]; // All Spice, Black Pepper, Cinnamon, etc.
    const bestsellers = bestsellerIds.map(id => getProductById(id)).filter(p => p);
    
    bestsellersGrid.innerHTML = bestsellers.map(product => `
        <div class="product-card">
            <div class="product-image">
                <img src="${productImageUrl(product.image)}" alt="${product.name}">
                <span class="bestseller-badge">⭐ Best Seller</span>
            </div>
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h3 class="product-name">${product.name}</h3>
                <div class="product-footer">
                    <span class="product-price">₦${product.price.toLocaleString()}</span>
                    <button class="add-to-cart-btn" onclick="addToCart(${product.id})">Add</button>
                </div>
            </div>
        </div>
    `).join('');
}
// Best sellers removed

// ============ TESTIMONIAL SLIDER ============
let currentSlide = 1;

function currentTestimonial(n) {
    showTestimonial(currentSlide = n);
}

function showTestimonial(n) {
    const slides = document.querySelectorAll('.testimonial-card');
    const dots = document.querySelectorAll('.dot');
    
    if (n > slides.length) {
        currentSlide = 1;
    } else if (n < 1) {
        currentSlide = slides.length;
    }
    
    slides.forEach(slide => slide.style.display = 'none');
    dots.forEach(dot => dot.classList.remove('active'));
    
    if (slides[currentSlide - 1]) {
        slides[currentSlide - 1].style.display = 'block';
        dots[currentSlide - 1].classList.add('active');
    }
}

// Auto-advance testimonials every 8 seconds
function autoAdvanceTestimonials() {
    currentSlide++;
    const slides = document.querySelectorAll('.testimonial-card');
    if (currentSlide > slides.length) {
        currentSlide = 1;
    }
    showTestimonial(currentSlide);
}

setInterval(autoAdvanceTestimonials, 8000);

// Helper: get product by id from ALL_PRODUCTS
function getProductById(id) {
    if (!Array.isArray(ALL_PRODUCTS)) return null;
    return ALL_PRODUCTS.find(p => p.id === id) || null;
}

// Make functions globally accessible
window.addToCart = addToCart;
window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart;
window.clearCart = clearCart;
window.getProductById = getProductById;
window.currentTestimonial = currentTestimonial;
window.showTestimonial = showTestimonial;
