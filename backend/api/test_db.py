"""
Test endpoint to verify database connection and products
"""
from flask import Blueprint, jsonify
import os

bp = Blueprint('test_db', __name__, url_prefix='/api/test')

@bp.route('/connection', methods=['GET'])
def test_connection():
    """Test database connection using SQLAlchemy"""
    try:
        import os
        from backend.app import db
        from backend.models.product import Product
        
        # Check environment variables
        env_vars = {
            'DATABASE_URL': 'set' if os.getenv("DATABASE_URL") else 'not_set',
            'POSTGRES_URL': 'set' if os.getenv("POSTGRES_URL") else 'not_set',
            'POSTGRES_PRISMA_URL': 'set' if os.getenv("POSTGRES_PRISMA_URL") else 'not_set',
            'VERCEL': os.getenv("VERCEL", "not_set"),
            'FLASK_ENV': os.getenv("FLASK_ENV", "not_set"),
        }
        
        # Get the actual database URL being used (masked for security)
        db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("POSTGRES_PRISMA_URL") or "localhost (default)"
        if db_url and db_url != "localhost (default)":
            # Mask the password in the URL
            if "@" in db_url:
                parts = db_url.split("@")
                if len(parts) == 2:
                    user_pass = parts[0].split("://")[-1]
                    if ":" in user_pass:
                        user = user_pass.split(":")[0]
                        db_url_masked = db_url.replace(user_pass, f"{user}:***")
                    else:
                        db_url_masked = db_url
                else:
                    db_url_masked = db_url
            else:
                db_url_masked = db_url
        else:
            db_url_masked = db_url
        
        # Test connection
        db.engine.connect()
        
        count = Product.query.count()
        products = Product.query.limit(5).all()
        
        return jsonify({
            'success': True,
            'method': 'sqlalchemy',
            'database_url_masked': db_url_masked[:100] + "..." if len(db_url_masked) > 100 else db_url_masked,
            'environment_variables': env_vars,
            'product_count': count,
            'sample_products': [{'id': p.id, 'name': p.name, 'category': p.category} for p in products],
            'message': 'Database connection successful'
        })
    except Exception as e:
        import traceback
        import os
        return jsonify({
            'success': False,
            'error': str(e),
            'environment_variables': {
                'DATABASE_URL': 'set' if os.getenv("DATABASE_URL") else 'not_set',
                'POSTGRES_URL': 'set' if os.getenv("POSTGRES_URL") else 'not_set',
                'VERCEL': os.getenv("VERCEL", "not_set"),
            },
            'traceback': traceback.format_exc()
        }), 500

@bp.route('/products', methods=['GET'])
def test_products_query():
    """Test products query - same as /api/products/ but with more debugging info"""
    try:
        from backend.app import db
        from backend.models.product import Product
        
        count = Product.query.count()
        all_products = Product.query.limit(10).all()
        
        return jsonify({
            'success': True,
            'total_products': count,
            'products_returned': len(all_products),
            'products': [{
                'id': p.id,
                'name': p.name,
                'category': p.category,
                'price': float(p.price) if p.price else None,
                'image_url': p.image_url[:50] + '...' if p.image_url and len(p.image_url) > 50 else (p.image_url or 'None')
            } for p in all_products]
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

