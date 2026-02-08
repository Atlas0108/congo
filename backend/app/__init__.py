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
    
    @app.route('/added-to-cart')
    def added_to_cart_page():
        return render_template('added_to_cart.html')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register error handlers to return JSON instead of HTML
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

