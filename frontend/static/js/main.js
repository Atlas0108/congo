// Main JavaScript for Congo

// Check authentication status
function checkAuth() {
    fetch('/api/users/me')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Not authenticated');
        })
        .then(user => {
            document.getElementById('auth-buttons').classList.add('hidden');
            document.getElementById('user-menu').classList.remove('hidden');
        })
        .catch(() => {
            document.getElementById('auth-buttons').classList.remove('hidden');
            document.getElementById('user-menu').classList.add('hidden');
        });
}

// Add to cart
function addToCart(productId) {
    fetch('/api/cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            updateCartCount();
            alert('Item added to cart!');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Please login to add items to cart');
    });
}

// Update cart count
function updateCartCount() {
    fetch('/api/cart/')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            return [];
        })
        .then(cart => {
            const count = cart.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cart-count').textContent = count;
        })
        .catch(() => {
            document.getElementById('cart-count').textContent = '0';
        });
}

// Logout
function logout() {
    fetch('/api/users/logout', {
        method: 'POST'
    })
    .then(() => {
        window.location.href = '/';
    });
}

// Handle header search
function handleHeaderSearch(event) {
    event.preventDefault();
    const headerSearchInput = document.getElementById('header-search-input');
    const mobileSearchInput = document.getElementById('mobile-search-input');
    const searchInput = headerSearchInput || mobileSearchInput;
    const searchTerm = searchInput ? searchInput.value.trim() : '';
    
    // Always navigate to products page with search query
    if (searchTerm) {
        window.location.href = `/products?search=${encodeURIComponent(searchTerm)}`;
    } else {
        window.location.href = '/products';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    updateCartCount();
    
    // Set search input value from URL parameter if on products page
    const urlParams = new URLSearchParams(window.location.search);
    const searchParam = urlParams.get('search');
    const headerSearchInput = document.getElementById('header-search-input');
    const mobileSearchInput = document.getElementById('mobile-search-input');
    
    if (headerSearchInput && searchParam) {
        headerSearchInput.value = searchParam;
    }
    if (mobileSearchInput && searchParam) {
        mobileSearchInput.value = searchParam;
    }
    
    // Mobile search toggle
    const mobileSearchToggle = document.getElementById('mobile-search-toggle');
    const mobileSearchContainer = document.getElementById('mobile-search-container');
    if (mobileSearchToggle && mobileSearchContainer) {
        mobileSearchToggle.addEventListener('click', () => {
            mobileSearchContainer.classList.toggle('hidden');
            if (!mobileSearchContainer.classList.contains('hidden')) {
                mobileSearchInput.focus();
            }
        });
    }
    
    // Sync mobile and desktop search inputs
    if (headerSearchInput && mobileSearchInput) {
        headerSearchInput.addEventListener('input', (e) => {
            mobileSearchInput.value = e.target.value;
        });
        mobileSearchInput.addEventListener('input', (e) => {
            headerSearchInput.value = e.target.value;
        });
    }
});

