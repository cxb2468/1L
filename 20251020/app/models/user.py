from app.models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 用户信息
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    billing_address = db.Column(db.Text)
    shipping_address = db.Column(db.Text)
    credit_card_info = db.Column(db.String(255))
    
    # 关系
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlists = db.relationship('Wishlist', backref='user', lazy=True)
    recently_viewed = db.relationship('RecentlyViewed', backref='user', lazy=True)
    
    # 权限相关
    is_admin = db.Column(db.Boolean, default=False)
    is_report_viewer = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'