from backend.app import db
from datetime import datetime

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_type = db.Column(db.String(50), nullable=False)  # e.g., 'Visa', 'Mastercard', 'American Express'
    last_four = db.Column(db.String(4), nullable=False)
    cardholder_name = db.Column(db.String(100), nullable=False)
    expiry_month = db.Column(db.Integer, nullable=True)
    expiry_year = db.Column(db.Integer, nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    is_expired = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='payment_methods')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'card_type': self.card_type,
            'last_four': self.last_four,
            'cardholder_name': self.cardholder_name,
            'expiry_month': self.expiry_month,
            'expiry_year': self.expiry_year,
            'is_default': self.is_default,
            'is_expired': self.is_expired,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

