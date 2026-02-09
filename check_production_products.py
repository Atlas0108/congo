#!/usr/bin/env python3
"""
Quick script to check products in production database
"""

import os
import sys
from backend.app import create_app, db
from backend.models.product import Product

# Load production env vars
if os.path.exists('.env.production'):
    from dotenv import load_dotenv
    load_dotenv('.env.production')

app = create_app()

with app.app_context():
    try:
        count = Product.query.count()
        print(f"Total products in database: {count}")
        
        if count > 0:
            products = Product.query.limit(5).all()
            print("\nFirst 5 products:")
            for p in products:
                print(f"  - ID: {p.id}, Name: {p.name}, Category: {p.category}, Image: {p.image_url[:50] if p.image_url else 'None'}...")
            
            # Check local filter
            local_products = Product.query.filter(Product.id % 2 == 0).count()
            print(f"\nLocal products (even IDs): {local_products}")
            
            # Check categories
            categories = db.session.query(Product.category).distinct().all()
            print(f"\nCategories: {[c[0] for c in categories if c[0]]}")
        else:
            print("No products found in database!")
            
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

