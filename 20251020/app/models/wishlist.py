from app.models import db
from datetime import datetime


class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_public = db.Column(db.Boolean, default=True)  # 公开或私有
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 关系
    wishlist_items = db.relationship('WishlistItem', backref='wishlist', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Wishlist {self.name} by User {self.user_id}>'


class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlists.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    def __repr__(self):
        return f'<WishlistItem Wishlist {self.wishlist_id} Book {self.book_id}>'