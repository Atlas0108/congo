from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    template_dir = os.path.join(base_dir, 'frontend', 'templates')
    static_dir = os.path.join(base_dir, 'frontend', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql+psycopg://localhost/congo_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from backend.api import products, users, orders, cart
    app.register_blueprint(products.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(cart.bp)
    
    # Register frontend routes
    from flask import render_template, jsonify
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/products')
    def products_page():
        return render_template('products.html')
    
    @app.route('/product/<int:product_id>')
    def product_detail(product_id):
        return render_template('product_detail.html', product_id=product_id)
    
    @app.route('/cart')
    def cart_page():
        return render_template('cart.html')
    
    @app.route('/login')
    def login_page():
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        return render_template('register.html')
    
    @app.route('/orders')
    def orders_page():
        return render_template('orders.html')
    
    @app.route('/account')
    def account_page():
        return render_template('account.html')
    
    @app.route('/account/addresses')
    def addresses_page():
        return render_template('addresses.html')
    
    @app.route('/account/addresses/new')
    def add_address_page():
        return render_template('add_address.html')
    
    @app.route('/account/payment-methods')
    def payment_methods_page():
        return render_template('payment_methods.html')
    
    @app.route('/account/security')
    def security_page():
        return render_template('security.html')
    
    @app.route('/about/local')
    def about_local_page():
        return render_template('about_local.html')
    
    @app.route('/merchant')
    def merchant_profile_page():
        return render_template('merchant_profile.html')
    
    @app.route('/added-to-cart')
    def added_to_cart_page():
        return render_template('added_to_cart.html')
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Add new columns/tables for merchant system if they don't exist
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            # Add role column to users table if it doesn't exist
            try:
                user_columns = [col['name'] for col in inspector.get_columns('users')]
                if 'role' not in user_columns:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'shopper'"))
                        conn.commit()
                    print("✓ Added role column to users table")
            except Exception as e:
                print(f"Note: Could not add role column (may already exist): {e}")
            
            # Add default_category column to users table if it doesn't exist
            try:
                user_columns = [col['name'] for col in inspector.get_columns('users')]
                if 'default_category' not in user_columns:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE users ADD COLUMN default_category VARCHAR(100)"))
                        conn.commit()
                    print("✓ Added default_category column to users table")
            except Exception as e:
                print(f"Note: Could not add default_category column (may already exist): {e}")
            
            # Add merchant_id column to products table if it doesn't exist
            try:
                product_columns = [col['name'] for col in inspector.get_columns('products')]
                if 'merchant_id' not in product_columns:
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE products ADD COLUMN merchant_id INTEGER REFERENCES users(id)'))
                        conn.commit()
                    print("✓ Added merchant_id column to products table")
            except Exception as e:
                print(f"Note: Could not add merchant_id column (may already exist): {e}")
            
            # Create merchant_profiles table if it doesn't exist
            if 'merchant_profiles' not in inspector.get_table_names():
                db.create_all()
                print("✓ Created merchant_profiles table")
        except Exception as e:
            # Tables might already exist
            print(f"Note: Schema migration check completed: {e}")
    
    # Register error handlers to return JSON instead of HTML
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

