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

def create_database():
    with app_module.app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")

if __name__ == '__main__':
    create_database()