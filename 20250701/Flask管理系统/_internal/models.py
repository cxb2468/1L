from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta
from extensions import db

# 获取北京时间
def beijing_time():
    """获取北京时间"""
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz)

# 用户角色表
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)  # 角色名，如管理员、普通员工
    users = db.relationship('User', backref='role', lazy=True)

# 用户表
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.String(200), default='')  # 业务模块权限
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    is_active = db.Column(db.Boolean, default=True)

# 合同信息表（精简版）
class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_type = db.Column(db.String(20), default='receipt')  # 合同类型：receipt(收款合同)、payment(付款合同)
    attachment = db.Column(db.String(200))  # 保留附件上传功能
    modified_by = db.Column(db.String(100))  # 修改人
    modified_at = db.Column(db.DateTime, default=beijing_time)  # 修改时间
    receipts = db.relationship('Receipt', backref='contract', lazy=True)
    payments = db.relationship('Payment', backref='contract', lazy=True)

# 收款记录表（精简版）
class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'))
    attachment = db.Column(db.String(200))  # 新增：收款记录附件
    modified_by = db.Column(db.String(100))  # 修改人
    modified_at = db.Column(db.DateTime, default=beijing_time)  # 修改时间

# 付款记录表（精简版）
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'))
    attachment = db.Column(db.String(200))  # 新增：付款记录附件
    modified_by = db.Column(db.String(100))  # 修改人
    modified_at = db.Column(db.DateTime, default=beijing_time)  # 修改时间

# 项目信息表（精简版）
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attachments = db.Column(db.Text)  # 新增：项目附件，JSON格式存储多个文件路径
    modified_by = db.Column(db.String(100))  # 修改人
    modified_at = db.Column(db.DateTime, default=beijing_time)  # 修改时间

# 人员信息表（精简版）
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modified_by = db.Column(db.String(100))  # 修改人
    modified_at = db.Column(db.DateTime, default=beijing_time)  # 修改时间

# 字段管理表
class FieldConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(50), nullable=False)  # 模块名称
    field_name = db.Column(db.String(50), nullable=False)   # 字段名称
    field_label = db.Column(db.String(100), nullable=False) # 字段标签
    field_type = db.Column(db.String(20), nullable=False)   # 字段类型
    is_required = db.Column(db.Boolean, default=False)      # 是否必填
    is_searchable = db.Column(db.Boolean, default=False)    # 是否可搜索
    is_exportable = db.Column(db.Boolean, default=True)     # 是否可导出
    is_importable = db.Column(db.Boolean, default=True)     # 是否可导入
    is_visible = db.Column(db.Boolean, default=True)        # 是否可见
    field_width = db.Column(db.Integer, default=100)        # 字段宽度
    field_order = db.Column(db.Integer, default=0)          # 字段顺序
    field_options = db.Column(db.Text)                      # 字段选项（JSON格式）
    validation_rules = db.Column(db.Text)                   # 验证规则（JSON格式）
    created_at = db.Column(db.DateTime, default=beijing_time)
    updated_at = db.Column(db.DateTime, default=beijing_time, onupdate=beijing_time)

# 字段值表（用于存储动态字段的值）
class FieldValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(50), nullable=False)  # 模块名称
    record_id = db.Column(db.Integer, nullable=False)       # 记录ID
    field_name = db.Column(db.String(50), nullable=False)   # 字段名称
    field_value = db.Column(db.Text)                        # 字段值
    created_at = db.Column(db.DateTime, default=beijing_time)
    updated_at = db.Column(db.DateTime, default=beijing_time, onupdate=beijing_time) 