# Admin module
from flask import Blueprint

# 创建 admin 蓝图
admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

# 导入路由
from admin import routes