from flask import Blueprint, request, jsonify, session
from backend.app import db
from backend.models.cart import CartItem
from backend.models.product import Product
import uuid

bp = Blueprint('cart', __name__, url_prefix='/api/cart')

def get_current_user_id():
    """Helper to get current user ID from session, verifying it exists"""
    user_id = session.get('user_id')
    if user_id:
        # Verify user still exists in database
        from backend.models.user import User
        user = User.query.get(user_id)
        if not user:
            # User doesn't exist, clear the session
            session.pop('user_id', None)
            return None
    return user_id

def get_or_create_session_id():
    """Get or create a session ID for guest users"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_cart_identifier():
    """Get cart identifier - user_id if logged in, session_id if guest"""
    user_id = get_current_user_id()
    if user_id:
        return {'user_id': user_id, 'session_id': None}
    else:
        return {'user_id': None, 'session_id': get_or_create_session_id()}

@bp.route('/', methods=['GET'])
def get_cart():
    """Get current user's or guest's cart"""
    cart_id = get_cart_identifier()
    
    if cart_id['user_id']:
        cart_items = CartItem.query.filter_by(user_id=cart_id['user_id']).order_by(CartItem.created_at.desc()).all()
    else:
        cart_items = CartItem.query.filter_by(session_id=cart_id['session_id']).order_by(CartItem.created_at.desc()).all()
    
    return jsonify([item.to_dict() for item in cart_items])

@bp.route('/', methods=['POST'])
def add_to_cart():
    """Add item to cart (works for both authenticated and guest users)"""
    try:
        cart_id = get_cart_identifier()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
        
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if product.stock < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Check if item already in cart
        if cart_id['user_id']:
            cart_item = CartItem.query.filter_by(
                user_id=cart_id['user_id'],
                product_id=product_id
            ).first()
        else:
            cart_item = CartItem.query.filter_by(
                session_id=cart_id['session_id'],
                product_id=product_id
            ).first()
        
        if cart_item:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return jsonify({'error': 'Insufficient stock'}), 400
        else:
            cart_item = CartItem(
                user_id=cart_id['user_id'],
                session_id=cart_id['session_id'],
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify(cart_item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@bp.route('/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """Update cart item quantity"""
    cart_id = get_cart_identifier()
    
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Verify ownership
    if cart_id['user_id']:
        if cart_item.user_id != cart_id['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        if cart_item.session_id != cart_id['session_id']:
            return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    quantity = data.get('quantity')
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        product = Product.query.get(cart_item.product_id)
        if product.stock < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        cart_item.quantity = quantity
    
    db.session.commit()
    return jsonify(cart_item.to_dict() if cart_item.quantity > 0 else {'message': 'Item removed'})

@bp.route('/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    """Remove item from cart"""
    cart_id = get_cart_identifier()
    
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Verify ownership
    if cart_id['user_id']:
        if cart_item.user_id != cart_id['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        if cart_item.session_id != cart_id['session_id']:
            return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'}), 200

