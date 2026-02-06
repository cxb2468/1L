import os

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/smart_production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # 分页配置
    PER_PAGE = 10