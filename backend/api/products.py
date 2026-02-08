from flask import Blueprint, request, jsonify, render_template
from backend.app import db
from backend.models.product import Product

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('/', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        category = request.args.get('category')
        search = request.args.get('search')
        local = request.args.get('local', '').lower() == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Product.query
        
        if category:
            query = query.filter(Product.category == category)
        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
        if local:
            # Filter for local products (even product IDs)
            query = query.filter(Product.id % 2 == 0)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items
        
        return jsonify({
            'products': [product.to_dict() for product in products],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'products': [], 'total': 0, 'page': 1, 'per_page': 20, 'pages': 0}), 500

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
def create_product():
    """Create a new product (admin only)"""
    data = request.get_json()
    
    product = Product(
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        stock=data.get('stock', 0),
        category=data.get('category'),
        image_url=data.get('image_url'),
        rating=data.get('rating', 0.0),
        review_count=data.get('review_count', 0)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique product categories"""
    categories = db.session.query(Product.category).distinct().all()
    return jsonify([cat[0] for cat in categories if cat[0]])

@bp.route('/populate-aliexpress', methods=['POST'])
def populate_aliexpress():
    """Populate products from AliExpress API (admin endpoint)"""
    from backend.utils.aliexpress import populate_products_from_aliexpress
    
    data = request.get_json() or {}
    count = data.get('count', 100)
    api_key = data.get('api_key')
    
    try:
        added_count = populate_products_from_aliexpress(api_key, count)
        return jsonify({
            'message': f'Successfully added {added_count} products',
            'count': added_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

