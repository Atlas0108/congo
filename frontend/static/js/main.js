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
            document.getElementById('username').textContent = user.username;
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    updateCartCount();
});

