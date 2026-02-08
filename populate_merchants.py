#!/usr/bin/env python3
"""
Script to create placeholder merchants and randomly assign them to products
"""

import os
import sys
import random
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import create_app, db
from backend.models.user import User
from backend.models.merchant import MerchantProfile
from backend.models.product import Product

# Placeholder merchant data
MERCHANT_DATA = [
    {
        'business_name': 'Local Goods Co.',
        'description': 'Your neighborhood source for quality local products. We partner with local artisans and businesses to bring you the best.',
        'city': 'San Francisco',
        'state': 'CA',
        'country': 'USA',
        'phone': '+1-415-555-0101',
        'email': 'info@localgoodsco.com',
        'website': 'https://localgoodsco.com'
    },
    {
        'business_name': 'Bay Area Marketplace',
        'description': 'Supporting local businesses in the Bay Area. Fast shipping and excellent customer service.',
        'city': 'Oakland',
        'state': 'CA',
        'country': 'USA',
        'phone': '+1-510-555-0202',
        'email': 'hello@bayareamarketplace.com',
        'website': 'https://bayareamarketplace.com'
    },
    {
        'business_name': 'Community Store',
        'description': 'Connecting you with amazing local products. Every purchase supports your community.',
        'city': 'Berkeley',
        'state': 'CA',
        'country': 'USA',
        'phone': '+1-510-555-0303',
        'email': 'contact@communitystore.com',
        'website': 'https://communitystore.com'
    },
    {
        'business_name': 'Golden Gate Goods',
        'description': 'Premium products from local San Francisco businesses. Quality you can trust.',
        'city': 'San Francisco',
        'state': 'CA',
        'country': 'USA',
        'phone': '+1-415-555-0404',
        'email': 'support@goldengategoods.com',
        'website': 'https://goldengategoods.com'
    },
    {
        'business_name': 'East Bay Essentials',
        'description': 'Essential products from East Bay businesses. Fast, reliable, local.',
        'city': 'Fremont',
        'state': 'CA',
        'country': 'USA',
        'phone': '+1-510-555-0505',
        'email': 'info@eastbayessentials.com',
        'website': 'https://eastbayessentials.com'
    },
    {
        'business_name': 'Peninsula Products',
        'description': 'Quality products from Peninsula businesses. Supporting local since 2020.',
        'city': 'Palo Alto',
        'state': 'CA',
        'country': 'USA',
        'phone': '+1-650-555-0606',
        'email': 'hello@peninsulaproducts.com',
        'website': 'https://peninsulaproducts.com'
    },
    {
        'business_name': 'North Bay Market',
        'description': 'Your source for North Bay local products. Fresh, local, delivered.',
        'city': 'Santa Rosa',
        'state': 'CA',
        'country': 'USA',
        'phone': '+1-707-555-0707',
        'email': 'contact@northbaymarket.com',
        'website': 'https://northbaymarket.com'
    },
    {
        'business_name': 'Valley Vendors',
        'description': 'Connecting Silicon Valley with quality local products. Innovation meets tradition.',
        'city': 'San Jose',
        'state': 'CA',
        'country': 'USA',
        'phone': '+1-408-555-0808',
        'email': 'info@valleyvendors.com',
        'website': 'https://valleyvendors.com'
    }
]

def create_merchants():
    """Create placeholder merchants"""
    app = create_app()
    
    with app.app_context():
        print("🏪 Creating placeholder merchants...\n")
        
        created_count = 0
        for i, merchant_data in enumerate(MERCHANT_DATA):
            # Check if merchant user already exists
            username = merchant_data['business_name'].lower().replace(' ', '_').replace('.', '').replace(',', '')
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                print(f"  ⏭️  Merchant '{merchant_data['business_name']}' already exists")
                continue
            
            # Create merchant user
            user = User(
                username=username,
                email=merchant_data['email'],
                first_name=merchant_data['business_name'].split()[0],
                last_name='Merchant',
                phone=merchant_data['phone'].replace('-', '').replace('+1-', ''),
                role='merchant'
            )
            user.set_password('merchant123')  # Default password
            
            db.session.add(user)
            db.session.flush()  # Get user.id
            
            # Create merchant profile
            address = f"{merchant_data['city']}, {merchant_data['state']} {merchant_data['country']}"
            merchant_profile = MerchantProfile(
                user_id=user.id,
                business_name=merchant_data['business_name'],
                description=merchant_data['description'],
                address=address,
                city=merchant_data['city'],
                state=merchant_data['state'],
                country=merchant_data['country'],
                phone=merchant_data['phone'],
                email=merchant_data['email'],
                website=merchant_data['website'],
                is_verified=random.choice([True, True, False]),  # 2/3 chance of being verified
                rating=round(random.uniform(3.5, 5.0), 1),
                review_count=random.randint(10, 500)
            )
            
            db.session.add(merchant_profile)
            created_count += 1
            print(f"  ✓ Created merchant: {merchant_data['business_name']} (User ID: {user.id})")
        
        db.session.commit()
        print(f"\n✅ Created {created_count} new merchants\n")
        
        return created_count

def assign_merchants_to_products():
    """Randomly assign merchants to products"""
    app = create_app()
    
    with app.app_context():
        print("🔗 Assigning merchants to products...\n")
        
        # Get all merchants
        merchants = User.query.filter_by(role='merchant').all()
        if not merchants:
            print("  ❌ No merchants found. Please create merchants first.")
            return 0
        
        # Get all products
        products = Product.query.all()
        if not products:
            print("  ❌ No products found.")
            return 0
        
        assigned_count = 0
        for product in products:
            # Randomly assign a merchant (80% chance of having a merchant)
            if random.random() < 0.8:
                merchant = random.choice(merchants)
                product.merchant_id = merchant.id
                assigned_count += 1
        
        db.session.commit()
        print(f"  ✓ Assigned merchants to {assigned_count} out of {len(products)} products\n")
        
        return assigned_count

def main():
    """Main function"""
    print("=" * 60)
    print("Merchant Population Script")
    print("=" * 60 + "\n")
    
    # Create merchants
    create_merchants()
    
    # Assign merchants to products
    assign_merchants_to_products()
    
    print("=" * 60)
    print("✅ Merchant population complete!")
    print("=" * 60)
    print("\nNote: Default password for all merchant accounts is 'merchant123'")

if __name__ == '__main__':
    main()

