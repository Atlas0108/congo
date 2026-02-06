from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    
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
    from flask import render_template
    
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
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

