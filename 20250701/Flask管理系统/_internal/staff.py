from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Staff, FieldValue
from dynamic_field_manager import DynamicFieldManager
from utils import permission_required
import os
import pandas as pd
import io
from datetime import datetime, timezone, timedelta
import urllib.parse

# 获取北京时间
def beijing_time():
    """获取北京时间"""
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz)

# 格式化北京时间的辅助函数
def format_beijing_time(dt):
    """格式化北京时间为字符串"""
    if not dt:
        return ''
    
    try:
        # 如果是UTC时间，转换为北京时间
        if dt.tzinfo is None:
            # 假设是UTC时间
            utc_tz = timezone.utc
            dt = dt.replace(tzinfo=utc_tz)
        
        beijing_tz = timezone(timedelta(hours=8))
        dt = dt.astimezone(beijing_tz)
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return str(dt)

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/')
@login_required
@permission_required('staff')
def staff_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '').strip()
    field = request.args.get('field', 'name')
    query = Staff.query
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('staff')
    dynamic_fields = field_manager.get_visible_fields()
    
    if q:
        # 动态字段搜索
        if field in [f['name'] for f in dynamic_fields]:
            # 在字段值表中搜索
            field_values = FieldValue.query.filter_by(
                module_name='staff',
                field_name=field
            ).filter(FieldValue.field_value.like(f'%{q}%')).all()
            record_ids = [fv.record_id for fv in field_values]
            if record_ids:
                query = query.filter(Staff.id.in_(record_ids))
            else:
                query = query.filter(Staff.id == -1)  # 无结果
    
    staffs = query.order_by(Staff.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # 为每个人员添加动态字段值
    for staff in staffs.items:
        staff.dynamic_fields = {}
        for dynamic_field in dynamic_fields:
            field_value = field_manager.get_field_value(staff.id, dynamic_field['name'])
            staff.dynamic_fields[dynamic_field['name']] = field_manager.format_field_value(field_value, dynamic_field)
    
    return render_template('staff_list.html', 
                         staffs=staffs, 
                         per_page=per_page, 
                         q=q, 
                         field=field,
                         dynamic_fields=dynamic_fields)

@staff_bp.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required('staff')
def staff_add():
    # 动态字段管理器
    field_manager = DynamicFieldManager('staff')
    dynamic_fields = field_manager.get_visible_fields()
    
    if request.method == 'POST':
        # 创建人员记录（只包含必要字段）
        staff = Staff(
            modified_by=current_user.username,
            modified_at=beijing_time()
        )
        db.session.add(staff)
        db.session.commit()
        
        # 处理动态字段
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            if field_value:
                field_manager.set_field_value(staff.id, field_name, field_value)
        
        flash('人员添加成功')
        
        # 获取返回URL参数，如果没有则返回列表页
        return_url = request.args.get('return_url')
        if return_url:
            return redirect(return_url)
        else:
            return redirect(url_for('staff.staff_list'))
    
    return render_template('staff_add.html', dynamic_fields=dynamic_fields)

@staff_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('staff')
def staff_edit(id):
    staff = Staff.query.get_or_404(id)
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('staff')
    dynamic_fields = field_manager.get_visible_fields()
    
    if request.method == 'POST':
        staff.modified_by = current_user.username
        staff.modified_at = beijing_time()
        db.session.commit()
        
        # 处理动态字段
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            field_manager.set_field_value(staff.id, field_name, field_value)
        
        flash('人员修改成功')
        
        # 获取返回URL参数，如果没有则返回列表页
        return_url = request.args.get('return_url')
        if return_url:
            return redirect(return_url)
        else:
            return redirect(url_for('staff.staff_list'))
    
    # 获取当前动态字段值
    current_values = {}
    for dynamic_field in dynamic_fields:
        field_value = field_manager.get_field_value(staff.id, dynamic_field['name'])
        current_values[dynamic_field['name']] = field_value
    
    return render_template('staff_edit.html', 
                         staff=staff, 
                         dynamic_fields=dynamic_fields,
                         current_values=current_values)

@staff_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('staff')
def staff_delete(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    flash('人员删除成功')
    return redirect(url_for('staff.staff_list'))

@staff_bp.route('/export')
@login_required
@permission_required('staff')
def staff_export():
    staffs = Staff.query.all()
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('staff')
    exportable_fields = field_manager.get_exportable_fields()
    
    data = []
    for staff in staffs:
        row = {}
        for field in exportable_fields:
            field_value = field_manager.get_field_value(staff.id, field['name'])
            row[field['label']] = field_manager.format_field_value(field_value, field)
        data.append(row)
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='人员信息导出.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@staff_bp.route('/import', methods=['POST'])
@login_required
@permission_required('staff')
def staff_import():
    file = request.files.get('import_file')
    if not file:
        flash('请选择要导入的文件')
        return redirect(url_for('staff.staff_list'))
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('staff')
    importable_fields = field_manager.get_importable_fields()
    
    df = pd.read_excel(file)
    for _, row in df.iterrows():
        try:
            # 创建人员记录
            staff = Staff(
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(staff)
            db.session.commit()
            
            # 处理动态字段
            for field in importable_fields:
                field_name = field['name']
                field_label = field['label']
                field_value = row.get(field_label, '')
                if pd.notna(field_value) and field_value != '':
                    field_manager.set_field_value(staff.id, field_name, str(field_value))
                    
        except Exception as e:
            print(f'导入失败: {e}, 行数据: {row.to_dict()}')
            continue
    
    flash('人员信息导入成功')
    return redirect(url_for('staff.staff_list'))

@staff_bp.route('/template')
@login_required
@permission_required('staff')
def staff_template():
    # 动态字段管理器
    field_manager = DynamicFieldManager('staff')
    importable_fields = field_manager.get_importable_fields()
    
    # 创建模板数据
    template_data = {}
    for field in importable_fields:
        template_data[field['label']] = ''
    
    output = io.BytesIO()
    df = pd.DataFrame([template_data])
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='人员导入模板.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 