from backend.app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='shopper')  # 'shopper' or 'merchant'
    default_category = db.Column(db.String(100), nullable=True)  # Default category preference (e.g., 'local')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        name = None
        if self.first_name or self.last_name:
            name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        elif self.username:
            name = self.username
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'phone': self.phone,
            'role': self.role,
            'default_category': self.default_category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

