from flask import Blueprint, request, jsonify, session
from backend.app import db
from backend.models.order import Order, OrderItem
from backend.models.cart import CartItem
from backend.models.product import Product

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def get_current_user_id():
    """Helper to get current user ID from session"""
    return session.get('user_id')

@bp.route('/', methods=['GET'])
def get_orders():
    """Get all orders for current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    order = Order.query.get_or_404(order_id)
    if order.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(order.to_dict())

@bp.route('/', methods=['POST'])
def create_order():
    """Create a new order from cart"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    shipping_address = data.get('shipping_address')
    payment_method_id = data.get('payment_method_id')
    
    if not shipping_address:
        return jsonify({'error': 'Shipping address is required'}), 400
    
    if not payment_method_id:
        return jsonify({'error': 'Payment method is required'}), 400
    
    # Verify payment method belongs to user
    from backend.models.payment_method import PaymentMethod
    payment_method = PaymentMethod.query.filter_by(id=payment_method_id, user_id=user_id).first()
    if not payment_method:
        return jsonify({'error': 'Invalid payment method'}), 400
    
    # Get cart items
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Calculate total
    total_amount = 0
    order_items_data = []
    
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        if not product or product.stock < cart_item.quantity:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
        
        item_total = float(product.price) * cart_item.quantity
        total_amount += item_total
        
        order_items_data.append({
            'product_id': product.id,
            'quantity': cart_item.quantity,
            'price': product.price
        })
    
    # Create order
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=shipping_address,
        payment_method_id=payment_method_id,
        status='pending'
    )
    db.session.add(order)
    db.session.flush()
    
    # Create order items and update stock
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.session.add(order_item)
        
        # Update product stock
        product = Product.query.get(item_data['product_id'])
        product.stock -= item_data['quantity']
    
    # Clear cart
    CartItem.query.filter_by(user_id=user_id).delete()
    
    db.session.commit()
    
    return jsonify(order.to_dict()), 201

