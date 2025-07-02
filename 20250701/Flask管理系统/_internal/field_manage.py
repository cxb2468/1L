from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import FieldConfig, FieldValue
from utils import permission_required
import json

field_bp = Blueprint('field', __name__, url_prefix='/field')

@field_bp.route('/')
@login_required
def field_list():
    """字段配置列表"""
    if not current_user.is_admin:
        flash('无权限访问字段管理')
        return redirect(url_for('index'))
    
    module_name = request.args.get('module', '')
    if module_name:
        fields = FieldConfig.query.filter_by(module_name=module_name).order_by(FieldConfig.field_order).all()
    else:
        fields = FieldConfig.query.order_by(FieldConfig.module_name, FieldConfig.field_order).all()
    
    # 获取所有模块
    modules = db.session.query(FieldConfig.module_name).distinct().all()
    modules = [m[0] for m in modules]
    
    return render_template('field_list.html', fields=fields, modules=modules, current_module=module_name)

@field_bp.route('/add', methods=['GET', 'POST'])
@login_required
def field_add():
    """添加字段配置"""
    if not current_user.is_admin:
        flash('无权限访问字段管理')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        module_name = request.form['module_name']
        field_name = request.form['field_name']
        field_label = request.form['field_label']
        field_type = request.form['field_type']
        is_required = 'is_required' in request.form
        is_searchable = 'is_searchable' in request.form
        is_exportable = 'is_exportable' in request.form
        is_importable = 'is_importable' in request.form
        is_visible = 'is_visible' in request.form
        field_width = int(request.form.get('field_width', 100))
        field_order = int(request.form.get('field_order', 0))
        field_options = request.form.get('field_options', '')
        validation_rules = request.form.get('validation_rules', '')
        
        # 检查字段是否已存在
        existing = FieldConfig.query.filter_by(module_name=module_name, field_name=field_name).first()
        if existing:
            flash('该模块下已存在同名字段')
            return render_template('field_add.html')
        
        field_config = FieldConfig(
            module_name=module_name,
            field_name=field_name,
            field_label=field_label,
            field_type=field_type,
            is_required=is_required,
            is_searchable=is_searchable,
            is_exportable=is_exportable,
            is_importable=is_importable,
            is_visible=is_visible,
            field_width=field_width,
            field_order=field_order,
            field_options=field_options,
            validation_rules=validation_rules
        )
        
        db.session.add(field_config)
        db.session.commit()
        flash('字段配置添加成功')
        return redirect(url_for('field.field_list', module=module_name))
    
    return render_template('field_add.html')

@field_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def field_edit(id):
    """编辑字段配置"""
    if not current_user.is_admin:
        flash('无权限访问字段管理')
        return redirect(url_for('index'))
    
    field_config = FieldConfig.query.get_or_404(id)
    
    if request.method == 'POST':
        field_config.field_label = request.form['field_label']
        field_config.field_type = request.form['field_type']
        field_config.is_required = 'is_required' in request.form
        field_config.is_searchable = 'is_searchable' in request.form
        field_config.is_exportable = 'is_exportable' in request.form
        field_config.is_importable = 'is_importable' in request.form
        field_config.is_visible = 'is_visible' in request.form
        field_config.field_width = int(request.form.get('field_width', 100))
        field_config.field_order = int(request.form.get('field_order', 0))
        field_config.field_options = request.form.get('field_options', '')
        field_config.validation_rules = request.form.get('validation_rules', '')
        
        db.session.commit()
        flash('字段配置更新成功')
        print(f"编辑字段后返回模块: {field_config.module_name}")  # 调试信息
        return redirect(url_for('field.field_list', module=field_config.module_name))
    
    return render_template('field_edit.html', field=field_config)

@field_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def field_delete(id):
    """删除字段配置"""
    if not current_user.is_admin:
        flash('无权限访问字段管理')
        return redirect(url_for('index'))
    
    field_config = FieldConfig.query.get_or_404(id)
    module_name = field_config.module_name
    
    # 删除相关的字段值
    FieldValue.query.filter_by(module_name=module_name, field_name=field_config.field_name).delete()
    
    # 删除字段配置
    db.session.delete(field_config)
    db.session.commit()
    flash('字段配置删除成功')
    return redirect(url_for('field.field_list', module=module_name))

@field_bp.route('/api/fields/<module_name>')
@login_required
def get_module_fields(module_name):
    """获取模块字段配置API"""
    fields = FieldConfig.query.filter_by(module_name=module_name, is_visible=True).order_by(FieldConfig.field_order).all()
    field_list = []
    for field in fields:
        field_data = {
            'name': field.field_name,
            'label': field.field_label,
            'type': field.field_type,
            'required': field.is_required,
            'searchable': field.is_searchable,
            'exportable': field.is_exportable,
            'importable': field.is_importable,
            'width': field.field_width,
            'order': field.field_order
        }
        if field.field_options:
            try:
                field_data['options'] = json.loads(field.field_options)
            except:
                field_data['options'] = []
        field_list.append(field_data)
    
    return jsonify(field_list)

@field_bp.route('/api/field-value/<module_name>/<int:record_id>/<field_name>', methods=['GET', 'POST'])
@login_required
def field_value_api(module_name, record_id, field_name):
    """字段值API"""
    if request.method == 'GET':
        field_value = FieldValue.query.filter_by(
            module_name=module_name, 
            record_id=record_id, 
            field_name=field_name
        ).first()
        return jsonify({'value': field_value.field_value if field_value else ''})
    
    elif request.method == 'POST':
        value = request.json.get('value', '')
        field_value = FieldValue.query.filter_by(
            module_name=module_name, 
            record_id=record_id, 
            field_name=field_name
        ).first()
        
        if field_value:
            field_value.field_value = value
        else:
            field_value = FieldValue(
                module_name=module_name,
                record_id=record_id,
                field_name=field_name,
                field_value=value
            )
            db.session.add(field_value)
        
        db.session.commit()
        return jsonify({'success': True}) 