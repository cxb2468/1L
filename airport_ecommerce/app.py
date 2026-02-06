from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from routes import main
    app.register_blueprint(main)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)