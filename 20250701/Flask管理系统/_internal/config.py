#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
默认配置文件（不要直接在这里改端口！）
如需自定义端口，请在 instance/config.py 中设置 PORT = 8080
"""

import os
import sys

def resource_path(relative_path):
    """ 获取打包后资源的绝对路径 """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Config:
    SECRET_KEY = 'your_secret_key'
    basedir = resource_path(".")
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{resource_path("data.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = resource_path('uploads')
    # 为每个表创建独立的附件文件夹
    CONTRACT_UPLOAD_FOLDER = resource_path('uploads/contracts')
    RECEIPT_UPLOAD_FOLDER = resource_path('uploads/receipts')
    PAYMENT_UPLOAD_FOLDER = resource_path('uploads/payments')
    PROJECT_UPLOAD_FOLDER = resource_path('uploads/projects')
    STAFF_UPLOAD_FOLDER = resource_path('uploads/staff')
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestConfig(Config):
    DEBUG = True
    PORT = 5001

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
} 