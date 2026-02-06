import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 直接导入 app.py 模块
import importlib.util
spec = importlib.util.spec_from_file_location("app_module", os.path.join(os.path.dirname(__file__), "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

from app.models import db
from app.models.user import User
from app.models.book import Book, Review
from app.models.order import Order, OrderItem, GiftOption
from app.models.cart import Cart, CartItem
from app.models.wishlist import Wishlist, WishlistItem
from app.models.recently_viewed import RecentlyViewed
from werkzeug.security import generate_password_hash

def init_database():
    with app_module.app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已存在管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 创建管理员用户
            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # 检查是否已存在报表查看用户
        report_user = User.query.filter_by(username='reporter').first()
        if not report_user:
            # 创建报表查看用户
            report_user = User(
                username='reporter',
                email='reporter@example.com',
                first_name='Report',
                last_name='Viewer',
                is_report_viewer=True
            )
            report_user.set_password('report123')
            db.session.add(report_user)
        
        # 检查是否已存在礼品选项
        if GiftOption.query.count() == 0:
            # 创建默认礼品选项
            gift_options = [
                GiftOption(
                    name='无礼品包装',
                    description='标准包装，不含礼品包装',
                    price=0.0
                ),
                GiftOption(
                    name='标准礼品包装',
                    description='精美礼品包装',
                    price=2.99
                ),
                GiftOption(
                    name='豪华礼品包装',
                    description='豪华礼品包装，附赠礼品卡',
                    price=5.99
                )
            ]
            
            for option in gift_options:
                db.session.add(option)
        
        # 提交所有更改
        db.session.commit()
        print("数据库初始化完成")

if __name__ == '__main__':
    init_database()