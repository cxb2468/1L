from app.models import db
from datetime import datetime


class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    publisher = db.Column(db.String(100))
    publication_date = db.Column(db.Date)
    pages = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    stock_quantity = db.Column(db.Integer, default=0)
    
    # 关系
    reviews = db.relationship('Review', backref='book', lazy=True)
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='book', lazy=True)
    
    def __repr__(self):
        return f'<Book {self.title}>'


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5星评级
    comment = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False)  # 需要管理员批准
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    def __repr__(self):
        return f'<Review for Book {self.book_id} by User {self.user_id}>'