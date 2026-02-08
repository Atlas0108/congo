from backend.app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Numeric(3, 2), default=0.0)
    review_count = db.Column(db.Integer, default=0)
    shipping_time = db.Column(db.String(50))  # e.g., "7-15 days", "15-30 days"
    shipping_cost = db.Column(db.Numeric(10, 2), default=0.0)
    aliexpress_id = db.Column(db.String(100))  # Store AliExpress product ID
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Merchant who sells this product
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    merchant = db.relationship('User', backref='products', lazy=True)
    
    def to_dict(self):
        try:
            merchant_id = self.merchant_id
        except (AttributeError, KeyError):
            merchant_id = None
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0,
            'stock': self.stock,
            'category': self.category,
            'image_url': self.image_url,
            'rating': float(self.rating) if self.rating else 0.0,
            'review_count': self.review_count,
            'shipping_time': self.shipping_time,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else 0.0,
            'aliexpress_id': self.aliexpress_id,
            'merchant_id': merchant_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

