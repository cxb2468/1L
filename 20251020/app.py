import os
from flask import Flask
from flask_login import LoginManager

# 导入数据库实例
from app.models import db
from app.models.user import User

# 创建Flask应用实例
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 数据库连接池优化 (仅适用于支持连接池的数据库)
# 对于SQLite，我们不需要这些高级连接池选项
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# 初始化数据库
db.init_app(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建必要的目录
os.makedirs(os.path.join(app.root_path, 'templates'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, 'static'), exist_ok=True)

# 注册蓝图
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.books import books_bp
from app.routes.cart import cart_bp
from app.routes.orders import orders_bp
from app.routes.wishlist import wishlist_bp
from app.routes.admin import admin_bp
from app.routes.reports import reports_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(reports_bp)

# 创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, threaded=True)