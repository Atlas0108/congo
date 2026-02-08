"""
AliExpress Product Fetcher
Fetches products from AliExpress API and populates the database
"""

import requests
import random
from backend.app import db
from backend.models.product import Product

# AliExpress API endpoints (using RapidAPI or similar service)
# For testing, we'll use a mock implementation that can be swapped with real API
ALIEXPRESS_API_BASE = "https://aliexpress-data.p.rapidapi.com"

def fetch_aliexpress_products(api_key=None, count=100):
    """
    Fetch products from AliExpress API
    
    Args:
        api_key: API key for AliExpress API (optional, will use mock data if not provided)
        count: Number of products to fetch (default: 100)
    
    Returns:
        List of product dictionaries
    """
    if not api_key:
        # Return mock data for testing
        return generate_mock_products(count)
    
    # Real API implementation would go here
    # This is a placeholder for when you have API credentials
    try:
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "aliexpress-data.p.rapidapi.com"
        }
        
        # Example API call (adjust based on actual API documentation)
        response = requests.get(
            f"{ALIEXPRESS_API_BASE}/product/search",
            headers=headers,
            params={"keyword": "", "page": "1", "pageSize": str(count)}
        )
        
        if response.status_code == 200:
            data = response.json()
            return parse_aliexpress_response(data)
        else:
            print(f"API Error: {response.status_code}")
            return generate_mock_products(count)
    except Exception as e:
        print(f"Error fetching from API: {e}")
        return generate_mock_products(count)

def generate_mock_products(count=100):
    """
    Generate mock AliExpress-style products for testing
    """
    categories = [
        "Electronics", "Home & Garden", "Fashion", "Sports & Outdoors",
        "Toys & Games", "Beauty & Health", "Automotive", "Tools"
    ]
    
    product_templates = [
        {
            "name": "Wireless Bluetooth Earbuds",
            "description": "High-quality wireless earbuds with noise cancellation, 30-hour battery life, and premium sound quality. Perfect for music lovers and professionals.",
            "base_price": 15.99
        },
        {
            "name": "Smart Watch Fitness Tracker",
            "description": "Multi-functional smartwatch with heart rate monitor, step counter, sleep tracking, and smartphone notifications. Waterproof design.",
            "base_price": 25.99
        },
        {
            "name": "LED Strip Lights RGB",
            "description": "16.4ft RGB LED strip lights with remote control, app control, and multiple color modes. Perfect for home decoration and ambiance.",
            "base_price": 12.99
        },
        {
            "name": "Phone Case with Stand",
            "description": "Protective phone case with built-in kickstand, shockproof design, and clear back to show your phone's design.",
            "base_price": 8.99
        },
        {
            "name": "Portable Power Bank",
            "description": "20000mAh portable charger with fast charging, dual USB ports, and LED indicator. Compatible with all smartphones.",
            "base_price": 18.99
        },
        {
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse with 2.4G connection, silent click, and long battery life. Perfect for office and home use.",
            "base_price": 9.99
        },
        {
            "name": "USB-C Cable",
            "description": "Fast charging USB-C cable, 6ft length, braided design, compatible with all USB-C devices.",
            "base_price": 6.99
        },
        {
            "name": "Laptop Stand",
            "description": "Adjustable aluminum laptop stand, ergonomic design, improves posture and cooling. Fits all laptop sizes.",
            "base_price": 19.99
        },
        {
            "name": "Desk Organizer",
            "description": "Bamboo desk organizer with multiple compartments for pens, papers, and office supplies. Eco-friendly design.",
            "base_price": 14.99
        },
        {
            "name": "Webcam Cover",
            "description": "Privacy webcam cover, slide design, fits all laptops and monitors. Protects your privacy.",
            "base_price": 4.99
        }
    ]
    
    shipping_options = [
        "7-15 days", "10-20 days", "15-30 days", "20-40 days", "5-12 days"
    ]
    
    products = []
    for i in range(count):
        template = random.choice(product_templates)
        variation = random.randint(1, 5)
        
        # Generate product name with variation
        name = f"{template['name']} - {['Standard', 'Pro', 'Premium', 'Deluxe', 'Ultra'][variation-1]} Version"
        
        # Vary the price
        price = round(template['base_price'] * (0.8 + random.random() * 0.4), 2)
        
        # Generate description with variations
        description = template['description']
        if random.random() > 0.5:
            description += " Includes free shipping and 1-year warranty."
        
        product = {
            "name": name,
            "description": description,
            "price": price,
            "stock": random.randint(10, 500),
            "category": random.choice(categories),
            "image_url": f"https://via.placeholder.com/400?text={name.replace(' ', '+')}",
            "rating": round(random.uniform(3.5, 5.0), 1),
            "review_count": random.randint(50, 5000),
            "shipping_time": random.choice(shipping_options),
            "shipping_cost": round(random.uniform(0, 5.99), 2),
            "aliexpress_id": f"ALX{random.randint(100000, 999999)}"
        }
        products.append(product)
    
    return products

def parse_aliexpress_response(data):
    """
    Parse AliExpress API response into product format
    (Adjust based on actual API response structure)
    """
    products = []
    # This would parse the actual API response
    # Placeholder implementation
    return products

def populate_products_from_aliexpress(api_key=None, count=100, app_context=None):
    """
    Fetch products from AliExpress and add them to the database
    
    Args:
        api_key: API key for AliExpress API (optional)
        count: Number of products to fetch
        app_context: Flask app context (optional, will create if not provided)
    """
    from flask import has_app_context
    
    # If we're not in an app context, create one
    if not has_app_context():
        from backend.app import create_app
        app = create_app()
        ctx = app.app_context()
        ctx.push()
        should_pop = True
    else:
        should_pop = False
    
    try:
        products_data = fetch_aliexpress_products(api_key, count)
        
        added_count = 0
        skipped_count = 0
        
        for product_data in products_data:
            # Check if product already exists
            existing = Product.query.filter_by(aliexpress_id=product_data.get('aliexpress_id')).first()
            if existing:
                skipped_count += 1
                continue
            
            product = Product(
                name=product_data['name'],
                description=product_data.get('description', ''),
                price=product_data['price'],
                stock=product_data.get('stock', 100),
                category=product_data.get('category', 'Uncategorized'),
                image_url=product_data.get('image_url'),
                rating=product_data.get('rating', 0.0),
                review_count=product_data.get('review_count', 0),
                shipping_time=product_data.get('shipping_time', '15-30 days'),
                shipping_cost=product_data.get('shipping_cost', 0.0),
                aliexpress_id=product_data.get('aliexpress_id')
            )
            
            db.session.add(product)
            added_count += 1
        
        db.session.commit()
        
        print(f"✅ Added {added_count} products to database")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} duplicate products")
        
        return added_count
    finally:
        if should_pop:
            ctx.pop()

