from flask import Blueprint, request, jsonify, session
from backend.app import db
from backend.models.cart import CartItem
from backend.models.product import Product

bp = Blueprint('cart', __name__, url_prefix='/api/cart')

def get_current_user_id():
    """Helper to get current user ID from session"""
    return session.get('user_id')

@bp.route('/', methods=['GET'])
def get_cart():
    """Get current user's cart"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify([item.to_dict() for item in cart_items])

@bp.route('/', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    product = Product.query.get_or_404(product_id)
    
    if product.stock < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock:
            return jsonify({'error': 'Insufficient stock'}), 400
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify(cart_item.to_dict()), 201

@bp.route('/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """Update cart item quantity"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != user_id:
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
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'}), 200

