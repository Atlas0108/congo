#!/usr/bin/env python3
"""
Database setup script for Congo
Run this script to initialize the database with sample data
"""

from backend.app import create_app, db
from backend.models.product import Product
from backend.models.user import User

def setup_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if products already exist
        if Product.query.count() == 0:
            # Add sample products
            sample_products = [
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
            ]
            
            for product in sample_products:
                db.session.add(product)
            
            db.session.commit()
            print(f"✓ Added {len(sample_products)} sample products")
        else:
            print("✓ Products already exist, skipping sample data")
        
        print("\n✓ Database setup complete!")
        print("\nYou can now run the application with: python run.py")

if __name__ == '__main__':
    setup_database()

