import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'japan.db')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

class DevelopmentConfig(Config):
    FLASK_DEBUG = True

class ProductionConfig(Config):
    FLASK_DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}