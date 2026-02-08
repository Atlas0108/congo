#!/usr/bin/env python3
"""
Script to populate database with placeholder products
Run this to add sample products while waiting for AliExpress credentials
"""

import os
from backend.app import create_app, db
from backend.models.product import Product
from backend.utils.image_search import fetch_images_for_products

def populate_placeholders():
    app = create_app()
    
    with app.app_context():
        # Recreate tables to ensure schema is up to date
        print("✓ Recreating database tables...")
        db.drop_all()
        db.create_all()
        print("✓ Database tables recreated")
        
        # Check if products already exist
        existing_count = Product.query.count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing products. Adding placeholder products...")
        else:
            print("✓ No existing products found. Adding placeholder products...")
        
        # Add placeholder products
        placeholder_products = [
            Product(
                name="Laptop Pro 15",
                description="High-performance laptop with 16GB RAM, 512GB SSD, and Intel i7 processor. Perfect for work and gaming.",
                price=1299.99,
                stock=25,
                category="Electronics",
                image_url="https://via.placeholder.com/300",
                rating=4.5,
                review_count=120,
                shipping_time="7-15 days",
                shipping_cost=0.00
            ),
            Product(
                name="Wireless Headphones",
                description="Premium noise-cancelling wireless headphones with 30-hour battery life and superior sound quality.",
                price=249.99,
                stock=50,
                category="Electronics",
                image_url="https://via.placeholder.com/300",
                rating=4.7,
                review_count=89,
                shipping_time="5-10 days",
                shipping_cost=0.00
            ),
            Product(
                name="Smart Coffee Maker",
                description="Programmable coffee maker with timer, auto-shutoff, and 12-cup capacity. Perfect for your morning routine.",
                price=79.99,
                stock=30,
                category="Home & Kitchen",
                image_url="https://via.placeholder.com/300",
                rating=4.3,
                review_count=45,
                shipping_time="10-20 days",
                shipping_cost=5.99
            ),
            Product(
                name="Running Shoes",
                description="Comfortable running shoes with cushioned sole and breathable mesh upper. Ideal for daily workouts.",
                price=89.99,
                stock=75,
                category="Sports & Outdoors",
                image_url="https://via.placeholder.com/300",
                rating=4.6,
                review_count=156,
                shipping_time="7-15 days",
                shipping_cost=0.00
            ),
            Product(
                name="Backpack",
                description="Durable backpack with multiple compartments, laptop sleeve, and water-resistant material.",
                price=49.99,
                stock=60,
                category="Fashion",
                image_url="https://via.placeholder.com/300",
                rating=4.4,
                review_count=78,
                shipping_time="10-20 days",
                shipping_cost=3.99
            ),
            Product(
                name="Smart Watch",
                description="Feature-rich smartwatch with fitness tracking, heart rate monitor, and smartphone notifications.",
                price=199.99,
                stock=40,
                category="Electronics",
                image_url="https://via.placeholder.com/300",
                rating=4.5,
                review_count=203,
                shipping_time="7-15 days",
                shipping_cost=0.00
            ),
            Product(
                name="Wireless Mouse",
                description="Ergonomic wireless mouse with precision tracking and long battery life. Compatible with all devices.",
                price=29.99,
                stock=100,
                category="Electronics",
                image_url="https://via.placeholder.com/300",
                rating=4.6,
                review_count=234,
                shipping_time="5-10 days",
                shipping_cost=0.00
            ),
            Product(
                name="Desk Lamp",
                description="LED desk lamp with adjustable brightness and color temperature. Perfect for home office.",
                price=39.99,
                stock=45,
                category="Home & Kitchen",
                image_url="https://via.placeholder.com/300",
                rating=4.4,
                review_count=67,
                shipping_time="10-20 days",
                shipping_cost=4.99
            ),
            Product(
                name="Yoga Mat",
                description="Non-slip yoga mat with extra cushioning. Ideal for yoga, pilates, and exercise routines.",
                price=24.99,
                stock=80,
                category="Sports & Outdoors",
                image_url="https://via.placeholder.com/300",
                rating=4.5,
                review_count=145,
                shipping_time="7-15 days",
                shipping_cost=0.00
            ),
            Product(
                name="Water Bottle",
                description="Insulated stainless steel water bottle keeps drinks cold for 24 hours or hot for 12 hours.",
                price=19.99,
                stock=120,
                category="Sports & Outdoors",
                image_url="https://via.placeholder.com/300",
                rating=4.7,
                review_count=189,
                shipping_time="5-10 days",
                shipping_cost=0.00
            ),
            Product(
                name="Bluetooth Speaker",
                description="Portable Bluetooth speaker with 360-degree sound and 12-hour battery life. Waterproof design.",
                price=59.99,
                stock=65,
                category="Electronics",
                image_url="https://via.placeholder.com/300",
                rating=4.6,
                review_count=178,
                shipping_time="7-15 days",
                shipping_cost=0.00
            ),
            Product(
                name="Phone Case",
                description="Protective phone case with shock absorption and raised edges for screen protection.",
                price=14.99,
                stock=200,
                category="Electronics",
                image_url="https://via.placeholder.com/300",
                rating=4.3,
                review_count=312,
                shipping_time="5-10 days",
                shipping_cost=0.00
            ),
            Product(
                name="Kitchen Knife Set",
                description="Professional 8-piece knife set with wooden block. Sharp, durable blades for all cooking needs.",
                price=89.99,
                stock=35,
                category="Home & Kitchen",
                image_url="https://via.placeholder.com/300",
                rating=4.5,
                review_count=98,
                shipping_time="10-20 days",
                shipping_cost=7.99
            ),
            Product(
                name="T-Shirt Pack",
                description="Pack of 3 comfortable cotton t-shirts in various colors. Soft, breathable fabric.",
                price=24.99,
                stock=150,
                category="Fashion",
                image_url="https://via.placeholder.com/300",
                rating=4.4,
                review_count=267,
                shipping_time="7-15 days",
                shipping_cost=0.00
            ),
            Product(
                name="Gaming Keyboard",
                description="Mechanical gaming keyboard with RGB backlighting and programmable keys. Fast response time.",
                price=79.99,
                stock=55,
                category="Electronics",
                image_url="https://via.placeholder.com/300",
                rating=4.6,
                review_count=156,
                shipping_time="7-15 days",
                shipping_cost=0.00
            ),
        ]
        
        # Fetch images for all products
        print("\n🖼️  Fetching product images from Google Image Search...")
        print("   (This may take a minute...)\n")
        
        # Get Google API credentials from environment (optional)
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        # Fetch images
        image_urls = fetch_images_for_products(
            placeholder_products,
            api_key=google_api_key,
            search_engine_id=google_search_engine_id,
            delay=0.3  # Small delay to avoid rate limiting
        )
        
        # Update product image URLs
        for product in placeholder_products:
            if product.name in image_urls:
                product.image_url = image_urls[product.name]
        
        print("\n✓ Images fetched successfully!\n")
        
        # Add products to database
        added_count = 0
        for product in placeholder_products:
            # Check if product already exists (by name)
            existing = Product.query.filter_by(name=product.name).first()
            if not existing:
                db.session.add(product)
                added_count += 1
        
        db.session.commit()
        print(f"✓ Added {added_count} placeholder products with images")
        print(f"✓ Total products in database: {Product.query.count()}")
        print("\n✅ Placeholder products populated successfully!")

if __name__ == '__main__':
    populate_placeholders()

