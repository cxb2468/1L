# Flask应用初始化文件
import os
from flask import Flask

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 创建Flask应用实例，指定模板目录和静态文件目录
app = Flask(__name__, 
             template_folder=os.path.join(project_root, 'templates'),
             static_folder=os.path.join(project_root, 'static'))

# 配置应用密钥（用于session加密）
app.secret_key = 'gold_price_monitor_secret_key_2026'

# 配置Werkzeug日志级别，移除HTTP请求日志
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

# 导入并注册 admin 蓝图
from admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# 导入路由
from app.routes import *

