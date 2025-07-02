#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask管理系统初始化脚本
用于打包后的程序初始化管理员账户和字段配置
"""

import os
import sys
from datetime import datetime

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    try:
        from app import app
        from models import db, User, Role
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # 创建所有表
            db.create_all()
            
            # 创建管理员角色
            admin_role = Role.query.filter_by(name='管理员').first()
            if not admin_role:
                admin_role = Role(name='管理员')
                db.session.add(admin_role)
                db.session.commit()
                print("✓ 已创建管理员角色")
            else:
                print("✓ 管理员角色已存在")
            
            # 创建初始管理员账户
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    role_id=admin_role.id,
                    is_active=True,
                    is_admin=True,
                    permissions='合同,项目,人员,收款,付款'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✓ 已创建管理员账户")
                print("  用户名: admin")
                print("  密码: admin123")
            else:
                print("✓ 管理员账户已存在")
            
            return True
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False

def init_field_config():
    """初始化字段配置"""
    print("正在初始化字段配置...")
    
    try:
        from app import app
        from models import db, FieldConfig
        
        # 预设的字段配置
        PRESET_FIELDS = [
            {
                "module_name": "contract",
                "field_name": "name",
                "field_label": "合同名称",
                "field_type": "text",
                "is_required": True,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 150,
                "field_order": 1,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "contract",
                "field_name": "party_a",
                "field_label": "甲方",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 2,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "contract",
                "field_name": "party_b",
                "field_label": "乙方",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 3,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "contract",
                "field_name": "contract_type",
                "field_label": "合同类别",
                "field_type": "select",
                "is_required": True,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 4,
                "field_options": "[\"收款合同\", \"付款合同\"]",
                "validation_rules": ""
            },
            {
                "module_name": "contract",
                "field_name": "amount",
                "field_label": "合同金额",
                "field_type": "number",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 5,
                "field_options": "",
                "validation_rules": "{\"min\": 0}"
            },
            {
                "module_name": "contract",
                "field_name": "sign_date",
                "field_label": "签订日期",
                "field_type": "date",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 6,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "contract",
                "field_name": "manager",
                "field_label": "负责人",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 100,
                "field_order": 7,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "contract",
                "field_name": "status",
                "field_label": "状态",
                "field_type": "select",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 80,
                "field_order": 8,
                "field_options": "[\"草稿\", \"执行中\", \"已完成\", \"已终止\"]",
                "validation_rules": ""
            },
            {
                "module_name": "contract",
                "field_name": "stdh",
                "field_label": "实体档号",
                "field_type": "text",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 100,
                "field_order": 9,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "contract",
                "field_name": "remark",
                "field_label": "备注",
                "field_type": "textarea",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 200,
                "field_order": 10,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "payment",
                "field_name": "manager",
                "field_label": "负责人",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 100,
                "field_order": 1,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "payment",
                "field_name": "amount",
                "field_label": "付款金额",
                "field_type": "number",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 2,
                "field_options": "",
                "validation_rules": "{\"min\": 0}"
            },
            {
                "module_name": "payment",
                "field_name": "is_paid",
                "field_label": "是否已付款",
                "field_type": "select",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 80,
                "field_order": 3,
                "field_options": "[\"是\",\"否\"]",
                "validation_rules": ""
            },
            {
                "module_name": "payment",
                "field_name": "is_invoiced",
                "field_label": "是否已开票",
                "field_type": "select",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 80,
                "field_order": 4,
                "field_options": "[\"是\",\"否\"]",
                "validation_rules": ""
            },
            {
                "module_name": "payment",
                "field_name": "record_date",
                "field_label": "付款日期",
                "field_type": "date",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 5,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "payment",
                "field_name": "remark",
                "field_label": "备注",
                "field_type": "textarea",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 200,
                "field_order": 6,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "project",
                "field_name": "name",
                "field_label": "项目名称",
                "field_type": "text",
                "is_required": True,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 150,
                "field_order": 1,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "project",
                "field_name": "owner",
                "field_label": "业主",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 2,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "project",
                "field_name": "address",
                "field_label": "项目地址",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 200,
                "field_order": 3,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "project",
                "field_name": "contact",
                "field_label": "联系人",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 100,
                "field_order": 4,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "project",
                "field_name": "phone",
                "field_label": "联系电话",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 5,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "project",
                "field_name": "prrject_manager",
                "field_label": "项目负责人",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 100,
                "field_order": 6,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "project",
                "field_name": "remark",
                "field_label": "备注",
                "field_type": "textarea",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 200,
                "field_order": 7,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "receipt",
                "field_name": "manager",
                "field_label": "负责人",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 100,
                "field_order": 1,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "receipt",
                "field_name": "amount",
                "field_label": "收款金额",
                "field_type": "number",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 2,
                "field_options": "",
                "validation_rules": "{\"min\": 0}"
            },
            {
                "module_name": "receipt",
                "field_name": "is_paid",
                "field_label": "是否已收款",
                "field_type": "select",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 80,
                "field_order": 3,
                "field_options": "[\"是\",\"否\"]",
                "validation_rules": ""
            },
            {
                "module_name": "receipt",
                "field_name": "is_invoiced",
                "field_label": "是否已开票",
                "field_type": "select",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 80,
                "field_order": 4,
                "field_options": "[\"是\",\"否\"]",
                "validation_rules": ""
            },
            {
                "module_name": "receipt",
                "field_name": "record_date",
                "field_label": "收款日期",
                "field_type": "date",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 5,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "receipt",
                "field_name": "remark",
                "field_label": "备注",
                "field_type": "textarea",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 200,
                "field_order": 6,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "staff",
                "field_name": "name",
                "field_label": "姓名",
                "field_type": "text",
                "is_required": True,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 100,
                "field_order": 1,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "staff",
                "field_name": "gender",
                "field_label": "性别",
                "field_type": "select",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 60,
                "field_order": 2,
                "field_options": "[\"男\", \"女\"]",
                "validation_rules": ""
            },
            {
                "module_name": "staff",
                "field_name": "id_number",
                "field_label": "身份证号",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 150,
                "field_order": 3,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "staff",
                "field_name": "phone",
                "field_label": "手机号",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 4,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "staff",
                "field_name": "bank_number",
                "field_label": "银行卡号",
                "field_type": "text",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 150,
                "field_order": 5,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "staff",
                "field_name": "bank_name",
                "field_label": "开户行",
                "field_type": "text",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 120,
                "field_order": 6,
                "field_options": "",
                "validation_rules": ""
            },
            {
                "module_name": "staff",
                "field_name": "staff_type",
                "field_label": "员工类别",
                "field_type": "select",
                "is_required": False,
                "is_searchable": True,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 100,
                "field_order": 7,
                "field_options": "[\"正式员工\", \"临时工\", \"外包人员\"]",
                "validation_rules": ""
            },
            {
                "module_name": "staff",
                "field_name": "remark",
                "field_label": "备注",
                "field_type": "textarea",
                "is_required": False,
                "is_searchable": False,
                "is_exportable": True,
                "is_importable": True,
                "is_visible": True,
                "field_width": 200,
                "field_order": 8,
                "field_options": "",
                "validation_rules": ""
            }
        ]
        
        with app.app_context():
            # 清空现有字段配置
            FieldConfig.query.delete()
            db.session.commit()
            
            # 添加预设字段配置
            for field_data in PRESET_FIELDS:
                field_config = FieldConfig(**field_data)
                db.session.add(field_config)
            
            db.session.commit()
            print("✓ 字段配置初始化完成")
            
            return True
    except Exception as e:
        print(f"✗ 字段配置初始化失败: {e}")
        return False

def create_init_script():
    """创建初始化脚本"""
    print("正在创建初始化脚本...")
    
    # Windows初始化脚本
    windows_script = '''@echo off
chcp 65001 >nul
title Flask管理系统初始化
echo ========================================
echo         Flask管理系统初始化
echo ========================================
echo.
echo 正在初始化系统...
echo.

python init_system.py

echo.
echo 初始化完成！
echo 请使用以下账户登录：
echo 用户名: admin
echo 密码: admin123
echo.
pause
'''
    
    with open('初始化系统.bat', 'w', encoding='utf-8') as f:
        f.write(windows_script)
    
    # Linux/Mac初始化脚本
    linux_script = '''#!/bin/bash
echo "========================================"
echo "         Flask管理系统初始化"
echo "========================================"
echo ""
echo "正在初始化系统..."
echo ""

python3 init_system.py

echo ""
echo "初始化完成！"
echo "请使用以下账户登录："
echo "用户名: admin"
echo "密码: admin123"
echo ""
'''
    
    with open('init_system.sh', 'w', encoding='utf-8') as f:
        f.write(linux_script)
    
    # 设置Linux脚本权限
    os.chmod('init_system.sh', 0o755)
    
    print("✓ 初始化脚本创建完成")

def main():
    """主函数"""
    print("Flask管理系统初始化工具")
    print("=" * 50)
    
    # 检查是否在打包环境中
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        print("检测到打包环境")
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"工作目录: {base_path}")
    
    # 初始化数据库
    if not init_database():
        print("数据库初始化失败")
        return
    
    # 初始化字段配置
    if not init_field_config():
        print("字段配置初始化失败")
        return
    
    # 创建初始化脚本
    create_init_script()
    
    print("\n" + "=" * 50)
    print("系统初始化完成！")
    print("=" * 50)
    print("默认管理员账户:")
    print("用户名: admin")
    print("密码: admin123")
    print("\n请及时修改默认密码！")
    print("\n现在可以启动系统了:")
    print("1. 双击 '启动系统.bat' 启动应用")
    print("2. 在浏览器中访问 http://localhost:5000")
    print("3. 使用上述账户登录")

if __name__ == "__main__":
    main() 