from flask import Blueprint, request, jsonify, session
from backend.app import db
from backend.models.user import User
from backend.models.address import Address
from backend.models.payment_method import PaymentMethod
from datetime import datetime

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Handle email or phone as identifier
    email = data.get('email')
    phone = data.get('phone')
    
    # If email_or_phone is provided, determine if it's email or phone
    email_or_phone = data.get('email_or_phone') or email
    if email_or_phone and '@' not in str(email_or_phone):
        # It's a phone number
        phone = email_or_phone
        email = None
    elif email_or_phone:
        email = email_or_phone
        phone = data.get('phone')  # Additional phone field
    
    # Generate username from email or use provided
    username = data.get('username')
    if not username:
        if email:
            username = email.split('@')[0]
        elif phone:
            username = f"user_{phone[-4:]}"  # Last 4 digits
        else:
            username = f"user_{db.session.query(User).count() + 1}"
    
    # Check if username exists and make it unique
    base_username = username
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Check if email exists
    if email and User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 400
    
    # Check if phone exists
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({'error': 'An account with this phone number already exists'}), 400
    
    # Require either email or phone
    if not email and not phone:
        return jsonify({'error': 'Email or phone number is required'}), 400
    
    # Validate password
    password = data.get('password')
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Parse first and last name from "Your name" field
    full_name = data.get('first_name', '').strip()
    first_name = full_name
    last_name = ''
    if ' ' in full_name:
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
    
    user = User(
        username=username,
        email=email,
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        address=data.get('address')
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    # Automatically log the user in after registration
    session['user_id'] = user.id
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201

@bp.route('/check-email', methods=['GET'])
def check_email():
    """Check if email already exists"""
    email = request.args.get('email')
    if not email:
        return jsonify({'exists': False}), 200
    
    exists = User.query.filter_by(email=email).first() is not None
    return jsonify({'exists': exists}), 200

@bp.route('/login', methods=['POST'])
def login():
    """Login user - supports username, email, or phone"""
    data = request.get_json()
    identifier = data.get('username') or data.get('email') or data.get('phone')
    password = data.get('password')
    
    if not identifier or not password:
        return jsonify({'error': 'Username/email/phone and password are required'}), 400
    
    # Try to find user by username, email, or phone
    user = None
    if '@' in identifier:
        user = User.query.filter_by(email=identifier).first()
    elif identifier.isdigit() or identifier.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').isdigit():
        # Phone number
        user = User.query.filter_by(phone=identifier).first()
    else:
        # Username
        user = User.query.filter_by(username=identifier).first()
    
    if user and user.check_password(password):
        # Merge guest cart with user cart before setting user_id
        guest_session_id = session.get('session_id')
        if guest_session_id:
            from backend.models.cart import CartItem
            # Get guest cart items
            guest_cart_items = CartItem.query.filter_by(session_id=guest_session_id).all()
            
            for guest_item in guest_cart_items:
                # Check if user already has this product in cart
                user_cart_item = CartItem.query.filter_by(
                    user_id=user.id,
                    product_id=guest_item.product_id
                ).first()
                
                if user_cart_item:
                    # Merge quantities
                    user_cart_item.quantity += guest_item.quantity
                    # Remove guest item
                    db.session.delete(guest_item)
                else:
                    # Transfer guest item to user
                    guest_item.user_id = user.id
                    guest_item.session_id = None
        
        session['user_id'] = user.id
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200

@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current logged in user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# Address endpoints
@bp.route('/addresses', methods=['GET'])
def get_addresses():
    """Get all addresses for the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    addresses = Address.query.filter_by(user_id=user_id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    return jsonify([address.to_dict() for address in addresses])

@bp.route('/addresses', methods=['POST'])
def create_address():
    """Create a new address for the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'address_line1', 'city', 'postal_code', 'country']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # If this is set as default, unset other defaults
    is_default = data.get('is_default', False)
    if is_default:
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    address = Address(
        user_id=user_id,
        name=data['name'],
        address_line1=data['address_line1'],
        address_line2=data.get('address_line2'),
        city=data['city'],
        state=data.get('state'),
        postal_code=data['postal_code'],
        country=data['country'],
        phone=data.get('phone'),
        is_default=is_default,
        delivery_instructions=data.get('delivery_instructions')
    )
    
    db.session.add(address)
    db.session.commit()
    
    return jsonify(address.to_dict()), 201

@bp.route('/addresses/<int:address_id>', methods=['GET'])
def get_address(address_id):
    """Get a specific address"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
    return jsonify(address.to_dict())

@bp.route('/addresses/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    """Update an address"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        address.name = data['name']
    if 'address_line1' in data:
        address.address_line1 = data['address_line1']
    if 'address_line2' in data:
        address.address_line2 = data.get('address_line2')
    if 'city' in data:
        address.city = data['city']
    if 'state' in data:
        address.state = data.get('state')
    if 'postal_code' in data:
        address.postal_code = data['postal_code']
    if 'country' in data:
        address.country = data['country']
    if 'phone' in data:
        address.phone = data.get('phone')
    if 'delivery_instructions' in data:
        address.delivery_instructions = data.get('delivery_instructions')
    
    # Handle default address
    if 'is_default' in data and data['is_default']:
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        address.is_default = True
    
    db.session.commit()
    return jsonify(address.to_dict())

@bp.route('/addresses/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    """Delete an address"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
    db.session.delete(address)
    db.session.commit()
    
    return jsonify({'message': 'Address deleted successfully'}), 200

@bp.route('/addresses/<int:address_id>/set-default', methods=['POST'])
def set_default_address(address_id):
    """Set an address as default"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
    
    # Unset other defaults
    Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    # Set this as default
    address.is_default = True
    db.session.commit()
    
    return jsonify(address.to_dict())

# Payment method endpoints
@bp.route('/payment-methods', methods=['GET'])
def get_payment_methods():
    """Get all payment methods for the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    payment_methods = PaymentMethod.query.filter_by(user_id=user_id).order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc()).all()
    return jsonify([pm.to_dict() for pm in payment_methods])

@bp.route('/payment-methods', methods=['POST'])
def create_payment_method():
    """Create a new payment method for the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['card_type', 'last_four', 'cardholder_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if this should be default
    if data.get('is_default'):
        PaymentMethod.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    # Check if expired
    is_expired = False
    if data.get('expiry_month') and data.get('expiry_year'):
        expiry_date = datetime(data['expiry_year'], data['expiry_month'], 1)
        if expiry_date < datetime.now():
            is_expired = True
    
    payment_method = PaymentMethod(
        user_id=user_id,
        card_type=data['card_type'],
        last_four=data['last_four'],
        cardholder_name=data['cardholder_name'],
        expiry_month=data.get('expiry_month'),
        expiry_year=data.get('expiry_year'),
        is_default=data.get('is_default', False),
        is_expired=is_expired
    )
    
    db.session.add(payment_method)
    db.session.commit()
    
    return jsonify(payment_method.to_dict()), 201

@bp.route('/payment-methods/<int:payment_method_id>', methods=['GET'])
def get_payment_method(payment_method_id):
    """Get a specific payment method"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    payment_method = PaymentMethod.query.filter_by(id=payment_method_id, user_id=user_id).first_or_404()
    return jsonify(payment_method.to_dict())

@bp.route('/payment-methods/<int:payment_method_id>', methods=['PUT'])
def update_payment_method(payment_method_id):
    """Update a payment method"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    payment_method = PaymentMethod.query.filter_by(id=payment_method_id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    if 'cardholder_name' in data:
        payment_method.cardholder_name = data['cardholder_name']
    if 'expiry_month' in data:
        payment_method.expiry_month = data['expiry_month']
    if 'expiry_year' in data:
        payment_method.expiry_year = data['expiry_year']
    
    # Check if expired
    if payment_method.expiry_month and payment_method.expiry_year:
        expiry_date = datetime(payment_method.expiry_year, payment_method.expiry_month, 1)
        payment_method.is_expired = expiry_date < datetime.now()
    
    if 'is_default' in data and data['is_default']:
        PaymentMethod.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        payment_method.is_default = True
    
    db.session.commit()
    return jsonify(payment_method.to_dict())

@bp.route('/payment-methods/<int:payment_method_id>', methods=['DELETE'])
def delete_payment_method(payment_method_id):
    """Delete a payment method"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    payment_method = PaymentMethod.query.filter_by(id=payment_method_id, user_id=user_id).first_or_404()
    db.session.delete(payment_method)
    db.session.commit()
    
    return jsonify({'message': 'Payment method deleted successfully'}), 200

@bp.route('/payment-methods/<int:payment_method_id>/set-default', methods=['POST'])
def set_default_payment_method(payment_method_id):
    """Set a payment method as default"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    payment_method = PaymentMethod.query.filter_by(id=payment_method_id, user_id=user_id).first_or_404()
    
    # Unset other defaults
    PaymentMethod.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    # Set this as default
    payment_method.is_default = True
    db.session.commit()
    
    return jsonify(payment_method.to_dict())

# Merchant endpoints
@bp.route('/merchants/<int:merchant_id>', methods=['GET'])
def get_merchant(merchant_id):
    """Get merchant profile by user ID"""
    from backend.models.merchant import MerchantProfile
    from backend.models.product import Product
    
    user = User.query.get_or_404(merchant_id)
    if user.role != 'merchant':
        return jsonify({'error': 'User is not a merchant'}), 404
    
    merchant_profile = MerchantProfile.query.filter_by(user_id=merchant_id).first()
    if not merchant_profile:
        return jsonify({'error': 'Merchant profile not found'}), 404
    
    # Get merchant's products
    products = Product.query.filter_by(merchant_id=merchant_id).limit(20).all()
    
    result = merchant_profile.to_dict()
    result['user'] = user.to_dict()
    result['products'] = [product.to_dict() for product in products]
    result['product_count'] = Product.query.filter_by(merchant_id=merchant_id).count()
    
    return jsonify(result)

