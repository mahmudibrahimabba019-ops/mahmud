// Halari House of Seasoning - Products from Backend API
let PRODUCTS = [];
let ALL_PRODUCTS = [];

// Fetch products from backend
async function loadProducts() {
    try {
        const response = await fetch('https://halari-backend.onrender.com/products');
        PRODUCTS = await response.json();
        ALL_PRODUCTS = PRODUCTS;
        console.log('Products loaded:', PRODUCTS);

        // Notify other scripts that products have been loaded
        try { window.dispatchEvent(new Event('productsLoaded')); } catch (e) { console.warn('Could not dispatch productsLoaded event', e); }

        return PRODUCTS;
    } catch (error) {
        console.error('Error loading products:', error);
        PRODUCTS = [];
        ALL_PRODUCTS = [];
        try { window.dispatchEvent(new Event('productsLoaded')); } catch (e) {}
        return [];
    }
}

// Function to display products on your webpage
function displayProductsOnPage(products) {
    // Get the container where products should be displayed
    const container = document.getElementById('products-container'); // Change this to your actual container ID
    
    if (!container) {
        console.log('Products container not found. Products:', products);
        return;
    }
    
    // Clear container
    container.innerHTML = '';
    
    // Loop through products and create HTML
    products.forEach(product => {
        const productHTML = `
            <div class="product-card" data-id="${product.id}">
                <h3><a href="product-detail.html?id=${product.id}">${product.name}</a></h3>
                <p class="category">${product.category}</p>
                <a class="btn-view" href="product-detail.html?id=${product.id}">View Details</a>
            </div>
        `;
        container.innerHTML += productHTML;
    });
}

// Load products when page loads
document.addEventListener('DOMContentLoaded', loadProducts);

// Example add to cart function (you can expand this)
function addToCart(productId) {
    // Prefer global cart if present
    try{
        if (window.addToCart && window.addToCart !== addToCart) {
            return window.addToCart(productId);
        }
    }catch(e){}
    // Fallback behavior when global cart API is not available
    const pid = (typeof productId === 'string' && !isNaN(productId)) ? Number(productId) : productId;
    const product = (Array.isArray(PRODUCTS) && PRODUCTS.find(p => String(p.id) === String(pid))) || null;
    const name = product && (product.name || product.product_name) ? (product.name || product.product_name) : `Item ${pid}`;
    const price = product ? Number(product.price || 0) : 0;

    // If a global Cart exists, use it
    try {
        if (window.cart && typeof window.cart.addItem === 'function') {
            window.cart.addItem({ id: pid, name: name, price: price, image: product ? product.image : null }, 1);
            showNotification && typeof showNotification === 'function' ? showNotification(`${name} added to cart!`) : alert(`${name} added to cart!`);
            return;
        }
    } catch (e) {}

    // Otherwise persist into localStorage legacy keys
    try {
        const existingRaw = localStorage.getItem('spices_cart') || localStorage.getItem('halari_cart') || localStorage.getItem('cart');
        let arr = [];
        if (existingRaw) {
            const parsed = JSON.parse(existingRaw);
            if (Array.isArray(parsed)) arr = parsed;
            else if (parsed && Array.isArray(parsed.items)) arr = parsed.items;
        }
        arr.push({ id: pid, product_name: name, name: name, price: price, quantity: 1, subtotal: price });
        const cartObj = { items: arr, subtotal: arr.reduce((s,i)=>s+Number(i.subtotal||0),0), delivery_fee: 3000, total: arr.reduce((s,i)=>s+Number(i.subtotal||0),0)+3000 };
        localStorage.setItem('cart', JSON.stringify(cartObj));
        localStorage.setItem('halari_cart', JSON.stringify(arr));
        localStorage.setItem('spices_cart', JSON.stringify(arr));
        alert(`${name} added to cart!`);
    } catch (e) {
        console.warn('Failed to fallback-add to cart', e);
        alert(`${name} added to cart!`);
    }
}


