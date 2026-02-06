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
                    review_count=120
                ),
                Product(
                    name="Wireless Headphones",
                    description="Premium noise-cancelling wireless headphones with 30-hour battery life and superior sound quality.",
                    price=249.99,
                    stock=50,
                    category="Electronics",
                    image_url="https://via.placeholder.com/300",
                    rating=4.7,
                    review_count=89
                ),
                Product(
                    name="Smart Coffee Maker",
                    description="Programmable coffee maker with timer, auto-shutoff, and 12-cup capacity. Perfect for your morning routine.",
                    price=79.99,
                    stock=30,
                    category="Home & Kitchen",
                    image_url="https://via.placeholder.com/300",
                    rating=4.3,
                    review_count=45
                ),
                Product(
                    name="Running Shoes",
                    description="Comfortable running shoes with cushioned sole and breathable mesh upper. Ideal for daily workouts.",
                    price=89.99,
                    stock=75,
                    category="Sports & Outdoors",
                    image_url="https://via.placeholder.com/300",
                    rating=4.6,
                    review_count=156
                ),
                Product(
                    name="Backpack",
                    description="Durable backpack with multiple compartments, laptop sleeve, and water-resistant material.",
                    price=49.99,
                    stock=60,
                    category="Fashion",
                    image_url="https://via.placeholder.com/300",
                    rating=4.4,
                    review_count=78
                ),
                Product(
                    name="Smart Watch",
                    description="Feature-rich smartwatch with fitness tracking, heart rate monitor, and smartphone notifications.",
                    price=199.99,
                    stock=40,
                    category="Electronics",
                    image_url="https://via.placeholder.com/300",
                    rating=4.5,
                    review_count=203
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

