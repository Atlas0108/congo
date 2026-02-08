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
            // Show logged in menu, hide guest menu
            const guestMenu = document.getElementById('account-menu-guest');
            const userMenu = document.getElementById('account-menu-user');
            const ordersLink = document.getElementById('orders-link');
            
            if (guestMenu) guestMenu.classList.add('hidden');
            if (userMenu) userMenu.classList.remove('hidden');
            if (ordersLink) ordersLink.classList.remove('hidden');
        })
        .catch(() => {
            // Show guest menu, hide logged in menu
            const guestMenu = document.getElementById('account-menu-guest');
            const userMenu = document.getElementById('account-menu-user');
            const ordersLink = document.getElementById('orders-link');
            
            if (guestMenu) guestMenu.classList.remove('hidden');
            if (userMenu) userMenu.classList.add('hidden');
            if (ordersLink) ordersLink.classList.add('hidden');
        });
}

// Add to cart (works for both logged in and guest users)
function addToCart(productId, redirectToConfirmation = false) {
    const button = document.querySelector(`[data-product-id="${productId}"]`);
    
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
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Failed to add item to cart');
            });
        }
        return response.json();
    })
    .then(data => {
        updateCartCount();
        
        // If redirectToConfirmation is true (from product detail page), redirect to confirmation page
        if (redirectToConfirmation) {
            window.location.href = `/added-to-cart?product_id=${productId}`;
            return;
        }
        
        // Otherwise, change button to "In cart" text (for home page, products page, etc.)
        if (button) {
            const isFullWidth = button.classList.contains('btn-primary-full');
            const wrapperClass = isFullWidth ? 'block' : 'inline-block';
            button.outerHTML = `<span class="text-gray-600 font-medium ${wrapperClass}" data-product-id="${productId}">In cart</span>`;
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        // Only show error if it's not a silent failure
        if (error.message && !error.message.includes('already')) {
            alert(error.message || 'Error adding item to cart. Please try again.');
        }
    });
}

// Check cart status and update button states
function updateCartButtonStates() {
    fetch('/api/cart/')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            return [];
        })
        .then(cart => {
            updateCartButtonStatesFromCart(cart);
        })
        .catch(() => {
            // Silently fail
        });
}

// Update cart count (works for both logged in and guest users)
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
            const cartCountEl = document.getElementById('cart-count');
            if (cartCountEl) {
                cartCountEl.textContent = count;
            }
            // Also update button states
            updateCartButtonStatesFromCart(cart);
        })
        .catch(() => {
            const cartCountEl = document.getElementById('cart-count');
            if (cartCountEl) {
                cartCountEl.textContent = '0';
            }
        });
}

// Update button states from cart data
function updateCartButtonStatesFromCart(cart) {
    const productIds = cart.map(item => item.product_id);
    // Update all buttons for products in cart
    productIds.forEach(productId => {
        const element = document.querySelector(`[data-product-id="${productId}"]`);
        if (element && element.tagName === 'BUTTON') {
            // Get button classes to preserve styling
            const isFullWidth = element.classList.contains('btn-primary-full');
            const sizeClass = element.classList.contains('btn-primary-lg') ? 'btn-primary-lg' : 
                            element.classList.contains('btn-primary-md') ? 'btn-primary-md' : 
                            element.classList.contains('btn-primary-sm') ? 'btn-primary-sm' : '';
            const wrapperClass = isFullWidth ? 'block' : 'inline-block';
            element.outerHTML = `<span class="text-gray-600 font-medium ${wrapperClass}" data-product-id="${productId}">In cart</span>`;
        }
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
    const headerCategoryValue = document.getElementById('header-category-value');
    const mobileCategoryValue = document.getElementById('mobile-category-value');
    
    const searchInput = headerSearchInput || mobileSearchInput;
    const categoryValue = headerCategoryValue || mobileCategoryValue;
    const searchTerm = searchInput ? searchInput.value.trim() : '';
    const category = categoryValue ? categoryValue.value : '';
    
    // Build URL with search and category
    let url = '/products?';
    const params = [];
    if (searchTerm) {
        params.push(`search=${encodeURIComponent(searchTerm)}`);
    }
    if (category === 'local') {
        params.push('local=true');
    } else if (category) {
        params.push(`category=${encodeURIComponent(category)}`);
    }
    
    if (params.length > 0) {
        window.location.href = url + params.join('&');
    } else {
        window.location.href = '/products';
    }
}

// Category dropdown functions
function toggleCategoryDropdown(type) {
    const dropdown = document.getElementById(`${type}-category-dropdown`);
    const otherDropdown = type === 'header' ? 
        document.getElementById('mobile-category-dropdown') : 
        document.getElementById('header-category-dropdown');
    
    // Close other dropdown if open
    if (otherDropdown) {
        otherDropdown.classList.add('hidden');
    }
    
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

function selectCategory(type, value, displayText) {
    const categoryValue = document.getElementById(`${type}-category-value`);
    const categoryDisplay = document.getElementById(`${type}-category-display`);
    const dropdown = document.getElementById(`${type}-category-dropdown`);
    
    if (categoryValue) {
        categoryValue.value = value;
    }
    if (categoryDisplay) {
        if (value === 'local') {
            categoryDisplay.innerHTML = `
                <span class="flex items-center gap-1.5">
                    <svg style="color: #ED6A5A;" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
                    </svg>
                    <span style="color: #0EAD69;">local</span>
                </span>
            `;
        } else {
            categoryDisplay.textContent = displayText;
        }
    }
    if (dropdown) {
        dropdown.classList.add('hidden');
    }
}

// Make functions globally available
window.toggleCategoryDropdown = toggleCategoryDropdown;
window.selectCategory = selectCategory;

// Global address selector variables
window.savedAddresses = [];
window.selectedAddressId = null;
window.ADDRESSES_TO_SHOW = 4;

// Load delivery location
function loadDeliveryLocation() {
    fetch('/api/users/addresses')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            return [];
        })
        .then(addresses => {
            window.savedAddresses = addresses;
            const deliveryLocation = document.getElementById('delivery-location');
            const cityZip = document.getElementById('delivery-city-zip');
            
            if (addresses.length > 0) {
                const defaultAddress = addresses.find(addr => addr.is_default) || addresses[0];
                if (defaultAddress) {
                    window.selectedAddressId = defaultAddress.id;
                    if (defaultAddress.city && defaultAddress.postal_code) {
                        cityZip.textContent = `${defaultAddress.city} ${defaultAddress.postal_code}`;
                        
                        // Update hero text if on home page
                        const heroTitle = document.getElementById('hero-title');
                        if (heroTitle && defaultAddress.city) {
                            heroTitle.textContent = `Shop Local, Support ${defaultAddress.city}`;
                        }
                        if (deliveryLocation) {
                            deliveryLocation.classList.remove('hidden');
                        }
                    }
                }
            }
        })
        .catch(() => {
            // Silently fail if addresses can't be loaded
        });
}

// Open address selector modal
function openAddressSelector() {
    const modal = document.getElementById('address-selector-modal');
    if (!modal) return;
    
    const addressList = document.getElementById('address-list');
    const addressCount = document.getElementById('address-count');
    
    // Reload addresses if needed
    fetch('/api/users/addresses')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            return [];
        })
            .then(addresses => {
                window.savedAddresses = addresses;
                if (addresses.length === 0) {
                    addressCount.textContent = 'Delivery addresses (0)';
                    addressList.innerHTML = '<p class="text-gray-500 text-center py-4">No addresses saved. <a href="/account/addresses/new" class="text-blue-600 hover:underline">Add an address</a></p>';
                    modal.classList.remove('hidden');
                    return;
                }
                
                addressCount.textContent = `Delivery addresses (${addresses.length})`;
                
                // Render addresses
                let html = '';
                const addressesToDisplay = addresses.slice(0, window.ADDRESSES_TO_SHOW);
                const hasMore = addresses.length > window.ADDRESSES_TO_SHOW;
                
                addressesToDisplay.forEach(address => {
                    const isSelected = address.id === window.selectedAddressId;
                const addressParts = [];
                if (address.address_line1) addressParts.push(address.address_line1);
                if (address.address_line2) addressParts.push(address.address_line2);
                if (address.city) {
                    let cityLine = address.city;
                    if (address.state) cityLine += ', ' + address.state;
                    if (address.postal_code) cityLine += ', ' + address.postal_code;
                    addressParts.push(cityLine);
                }
                if (address.country) addressParts.push(address.country);
                
                html += `
                    <div class="border border-gray-200 rounded-lg p-4 ${isSelected ? 'border-blue-500 bg-blue-50' : ''}">
                        <label class="flex items-start cursor-pointer">
                            <input type="radio" name="address_radio" value="${address.id}" ${isSelected ? 'checked' : ''} 
                                   onchange="updateAddressSelection(${address.id})" 
                                   class="mt-1 mr-3 w-4 h-4 text-blue-600">
                            <div class="flex-1">
                                <div class="font-semibold mb-1">${address.name}</div>
                                <div class="text-sm text-gray-700 mb-1">${addressParts.join(', ')}</div>
                                ${address.phone ? `<div class="text-sm text-gray-700 mb-2">${address.phone}</div>` : ''}
                                <div class="flex items-center gap-2 text-sm text-blue-600">
                                    <a href="/account/addresses" class="hover:underline">Edit address</a>
                                    ${address.phone ? '<span>|</span><a href="#" onclick="addDeliveryInstructions(' + address.id + '); return false;" class="hover:underline">Add delivery instructions</a>' : ''}
                                </div>
                            </div>
                        </label>
                    </div>
                `;
            });
            
            if (hasMore) {
                html += `
                    <button type="button" onclick="showMoreAddresses()" class="text-blue-600 hover:underline text-sm flex items-center gap-1">
                        Show more addresses
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </button>
                `;
            }
            
            addressList.innerHTML = html;
            modal.classList.remove('hidden');
        })
        .catch(() => {
            // Silently fail
        });
}

function closeAddressSelector() {
    const modal = document.getElementById('address-selector-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function updateAddressSelection(addressId) {
    window.selectedAddressId = addressId;
    // Update visual selection in the modal
    const addressList = document.getElementById('address-list');
    if (addressList) {
        const addressCards = addressList.querySelectorAll('.border');
        addressCards.forEach(card => {
            const radio = card.querySelector('input[type="radio"]');
            if (radio && parseInt(radio.value) === addressId) {
                card.classList.add('border-blue-500', 'bg-blue-50');
                card.classList.remove('border-gray-200');
            } else {
                card.classList.remove('border-blue-500', 'bg-blue-50');
                card.classList.add('border-gray-200');
            }
        });
    }
}

function confirmAddressSelection() {
    const selectedRadio = document.querySelector('input[name="address_radio"]:checked');
    if (!selectedRadio) {
        alert('Please select an address');
        return;
    }
    
    const addressId = parseInt(selectedRadio.value);
    const address = window.savedAddresses.find(addr => addr.id === addressId);
    if (address) {
        window.selectedAddressId = addressId;
        
        // Update delivery location display in header
        const cityZip = document.getElementById('delivery-city-zip');
        const deliveryLocation = document.getElementById('delivery-location');
        if (cityZip && address.city && address.postal_code) {
            cityZip.textContent = `${address.city} ${address.postal_code}`;
            if (deliveryLocation) {
                deliveryLocation.classList.remove('hidden');
            }
        }
        
        // Update hero text if on home page
        const heroTitle = document.getElementById('hero-title');
        if (heroTitle && address.city) {
            heroTitle.textContent = `Shop Local, Support ${address.city}`;
        }
        
        // Update checkout address if on cart page
        const addressDetails = document.getElementById('address-details');
        const shippingAddress = document.getElementById('shipping_address');
        if (addressDetails && shippingAddress) {
            // Format address for display
            let addressHtml = `<div class="font-semibold mb-1">${address.name}</div>`;
            const addressParts = [];
            if (address.address_line1) addressParts.push(address.address_line1);
            if (address.address_line2) addressParts.push(address.address_line2);
            if (address.city) {
                let cityLine = address.city;
                if (address.state) cityLine += ', ' + address.state;
                if (address.postal_code) cityLine += ', ' + address.postal_code;
                addressParts.push(cityLine);
            }
            if (address.country) addressParts.push(address.country);
            addressHtml += `<div>${addressParts.join(', ')}</div>`;
            if (address.phone) {
                addressHtml += `<div class="mt-1">${address.phone}</div>`;
            }
            
            addressDetails.innerHTML = addressHtml;
            
            // Format address for submission
            const formattedAddress = addressParts.join('\n');
            shippingAddress.value = formattedAddress;
            
            const selectedAddressIdInput = document.getElementById('selected_address_id');
            if (selectedAddressIdInput) {
                selectedAddressIdInput.value = address.id;
            }
        }
        
        closeAddressSelector();
    }
}

function showMoreAddresses() {
    const addressList = document.getElementById('address-list');
    if (!addressList) return;
    
    let html = '';
    
    window.savedAddresses.forEach(address => {
        const isSelected = address.id === window.selectedAddressId;
        const addressParts = [];
        if (address.address_line1) addressParts.push(address.address_line1);
        if (address.address_line2) addressParts.push(address.address_line2);
        if (address.city) {
            let cityLine = address.city;
            if (address.state) cityLine += ', ' + address.state;
            if (address.postal_code) cityLine += ', ' + address.postal_code;
            addressParts.push(cityLine);
        }
        if (address.country) addressParts.push(address.country);
        
        html += `
            <div class="border border-gray-200 rounded-lg p-4 ${isSelected ? 'border-blue-500 bg-blue-50' : ''}">
                <label class="flex items-start cursor-pointer">
                    <input type="radio" name="address_radio" value="${address.id}" ${isSelected ? 'checked' : ''} 
                           onchange="updateAddressSelection(${address.id})" 
                           class="mt-1 mr-3 w-4 h-4 text-blue-600">
                    <div class="flex-1">
                        <div class="font-semibold mb-1">${address.name}</div>
                        <div class="text-sm text-gray-700 mb-1">${addressParts.join(', ')}</div>
                        ${address.phone ? `<div class="text-sm text-gray-700 mb-2">${address.phone}</div>` : ''}
                        <div class="flex items-center gap-2 text-sm text-blue-600">
                            <a href="/account/addresses" class="hover:underline">Edit address</a>
                            ${address.phone ? '<span>|</span><a href="#" onclick="addDeliveryInstructions(' + address.id + '); return false;" class="hover:underline">Add delivery instructions</a>' : ''}
                        </div>
                    </div>
                </label>
            </div>
        `;
    });
    
    addressList.innerHTML = html;
}

function addDeliveryInstructions(addressId) {
    // TODO: Implement delivery instructions
    alert('Delivery instructions functionality coming soon!');
}

// Make functions globally available
window.openAddressSelector = openAddressSelector;
window.closeAddressSelector = closeAddressSelector;
window.updateAddressSelection = updateAddressSelection;
window.confirmAddressSelection = confirmAddressSelection;
window.showMoreAddresses = showMoreAddresses;
window.addDeliveryInstructions = addDeliveryInstructions;

// Load categories into header dropdowns
function loadHeaderCategories() {
    fetch('/api/products/categories')
        .then(response => response.json())
        .then(categories => {
            const headerOptions = document.getElementById('header-category-options');
            const mobileOptions = document.getElementById('mobile-category-options');
            
            categories.forEach(category => {
                if (headerOptions) {
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-gray-900';
                    button.textContent = category;
                    button.onclick = () => selectCategory('header', category, category);
                    headerOptions.appendChild(button);
                }
                if (mobileOptions) {
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-gray-900';
                    button.textContent = category;
                    button.onclick = () => selectCategory('mobile', category, category);
                    mobileOptions.appendChild(button);
                }
            });
        })
        .catch(() => {
            // Silently fail if categories can't be loaded
        });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    updateCartCount();
    updateCartButtonStates();
    loadDeliveryLocation();
    loadHeaderCategories();
    
    // Close category dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        const headerDropdown = document.getElementById('header-category-dropdown');
        const mobileDropdown = document.getElementById('mobile-category-dropdown');
        const headerButton = document.getElementById('header-category-button');
        const mobileButton = document.getElementById('mobile-category-button');
        
        if (headerDropdown && !headerDropdown.contains(e.target) && !headerButton.contains(e.target)) {
            headerDropdown.classList.add('hidden');
        }
        if (mobileDropdown && !mobileDropdown.contains(e.target) && !mobileButton.contains(e.target)) {
            mobileDropdown.classList.add('hidden');
        }
    });
    
    // Close modal when clicking outside
    const modal = document.getElementById('address-selector-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target.id === 'address-selector-modal') {
                closeAddressSelector();
            }
        });
    }
    
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

