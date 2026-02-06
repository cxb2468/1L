from app.models import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    
    # 地址信息
    billing_address = db.Column(db.Text, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    credit_card_info = db.Column(db.String(255), nullable=False)
    
    # 礼品选项
    gift_wrapping = db.Column(db.Boolean, default=False)
    gift_message = db.Column(db.Text)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 关系
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id} by User {self.user_id}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # 下单时的价格
    
    # 外键
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    def __repr__(self):
        return f'<OrderItem Order {self.order_id} Book {self.book_id}>'


class GiftOption(db.Model):
    __tablename__ = 'gift_options'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 如"标准包装", "精美包装"
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<GiftOption {self.name}>'