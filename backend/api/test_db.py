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
        from backend.app import db
        from backend.models.product import Product
        
        # Test connection
        db.engine.connect()
        
        count = Product.query.count()
        products = Product.query.limit(5).all()
        
        return jsonify({
            'success': True,
            'method': 'sqlalchemy',
            'database_url': os.getenv("DATABASE_URL", "not_set")[:50] + "..." if os.getenv("DATABASE_URL") else "not_set",
            'product_count': count,
            'sample_products': [{'id': p.id, 'name': p.name, 'category': p.category} for p in products],
            'message': 'Database connection successful'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
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

