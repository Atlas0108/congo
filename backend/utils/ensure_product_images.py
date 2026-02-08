"""
Utility to ensure all products have images
Fetches images from Google Image Search for products that don't have image URLs
"""

import os
from backend.models.product import Product
from backend.utils.image_search import fetch_images_for_products

def ensure_product_images(app_context=None, force_refresh=False):
    """
    Ensure all products in the database have image URLs.
    Fetches images for products that don't have them.
    
    Args:
        app_context: Flask app context (optional)
        force_refresh: If True, refresh images for all products (default: False)
    
    Returns:
        int: Number of products updated with images
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
        # Get products that need images
        if force_refresh:
            products = Product.query.all()
        else:
            from sqlalchemy import or_
            products = Product.query.filter(
                or_(
                    Product.image_url.is_(None),
                    Product.image_url == '',
                    Product.image_url.like('%placeholder%')
                )
            ).all()
        
        if not products:
            if should_pop:
                ctx.pop()
            return 0
        
        print(f"🖼️  Found {len(products)} products that need images...")
        
        # Get Google API credentials from environment (optional)
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        # Fetch images
        image_urls = fetch_images_for_products(
            products,
            api_key=google_api_key,
            search_engine_id=google_search_engine_id,
            delay=0.3
        )
        
        # Update products with images
        updated_count = 0
        from backend.app import db
        
        for product in products:
            if product.name in image_urls and image_urls[product.name]:
                product.image_url = image_urls[product.name]
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print(f"✅ Updated {updated_count} products with images")
        else:
            print("ℹ️  No products needed image updates")
        
        return updated_count
        
    finally:
        if should_pop:
            ctx.pop()

