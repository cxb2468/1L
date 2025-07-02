from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, send_from_directory
from flask_login import login_required, current_user
from extensions import db
from models import Project, FieldValue
from datetime import datetime, timezone, timedelta
from utils import permission_required
from dynamic_field_manager import DynamicFieldManager
import pandas as pd
import io
import numpy as np
import os
import json
from urllib.parse import unquote

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

project_bp = Blueprint('project', __name__, url_prefix='/project')

def is_allowed_file(filename):
    """检查文件类型是否允许"""
    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_filename(project_name, original_filename):
    """生成新的文件名"""
    if not project_name:
        project_name = "未命名项目"
    
    # 清理项目名称，移除特殊字符
    safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    # 获取文件扩展名
    file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    # 生成新文件名：项目名称_原文件名
    new_filename = f"{safe_name}_{original_filename}"
    
    return new_filename

@project_bp.route('/')
@login_required
@permission_required('project')
def project_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '').strip()
    field = request.args.get('field', 'name')
    query = Project.query
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('project')
    dynamic_fields = field_manager.get_visible_fields()
    
    if q:
        # 动态字段搜索
        if field in [f['name'] for f in dynamic_fields]:
            # 在字段值表中搜索
            field_values = FieldValue.query.filter_by(
                module_name='project',
                field_name=field
            ).filter(FieldValue.field_value.like(f'%{q}%')).all()
            record_ids = [fv.record_id for fv in field_values]
            if record_ids:
                query = query.filter(Project.id.in_(record_ids))
            else:
                query = query.filter(Project.id == -1)  # 无结果
    
    projects = query.order_by(Project.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # 为每个项目添加动态字段值和附件信息
    for project in projects.items:
        project.dynamic_fields = {}
        for dynamic_field in dynamic_fields:
            field_value = field_manager.get_field_value(project.id, dynamic_field['name'])
            project.dynamic_fields[dynamic_field['name']] = field_manager.format_field_value(field_value, dynamic_field)
        
        # 解析附件信息
        project.attachment_list = []
        if project.attachments:
            try:
                project.attachment_list = json.loads(project.attachments)
            except:
                project.attachment_list = []
    
    return render_template('project_list.html', 
                         projects=projects, 
                         per_page=per_page, 
                         q=q, 
                         field=field,
                         dynamic_fields=dynamic_fields)

@project_bp.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required('project')
def project_add():
    # 动态字段管理器
    field_manager = DynamicFieldManager('project')
    dynamic_fields = field_manager.get_visible_fields()
    
    if request.method == 'POST':
        # 处理附件上传
        files = request.files.getlist('attachments')
        uploaded_files = []
        
        if files and any(f.filename for f in files):
            # 先创建项目记录以获取ID
            project = Project(
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(project)
            db.session.commit()
            
            # 获取项目名称用于创建文件夹
            project_name = ""
            for dynamic_field in dynamic_fields:
                if dynamic_field['name'] == 'name':
                    project_name = request.form.get(f'dynamic_{dynamic_field["name"]}', '')
                    break
            
            # 创建项目文件夹
            if project_name:
                # 清理文件夹名称，移除特殊字符
                safe_folder_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                project_folder = os.path.join(current_app.config['PROJECT_UPLOAD_FOLDER'], safe_folder_name)
                os.makedirs(project_folder, exist_ok=True)
                
                # 处理每个上传的文件
                for file in files:
                    if file and file.filename:
                        # 检查文件类型
                        if not is_allowed_file(file.filename):
                            flash(f'不支持的文件类型：{file.filename}，请上传PDF、Word、Excel、图片或文本文件')
                            continue
                        
                        # 生成新文件名
                        new_filename = generate_filename(project_name, file.filename)
                        upload_path = os.path.join(project_folder, new_filename)
                        
                        # 保存文件
                        file.save(upload_path)
                        uploaded_files.append(os.path.join(safe_folder_name, new_filename))
            else:
                # 如果没有项目名称，使用默认路径
                for file in files:
                    if file and file.filename:
                        # 检查文件类型
                        if not is_allowed_file(file.filename):
                            flash(f'不支持的文件类型：{file.filename}，请上传PDF、Word、Excel、图片或文本文件')
                            continue
                        
                        # 生成新文件名
                        new_filename = generate_filename("未命名项目", file.filename)
                        upload_path = os.path.join(current_app.config['PROJECT_UPLOAD_FOLDER'], new_filename)
                        
                        # 保存文件
                        file.save(upload_path)
                        uploaded_files.append(new_filename)
            
            # 保存附件信息到数据库
            if uploaded_files:
                project.attachments = json.dumps(uploaded_files, ensure_ascii=False)
                db.session.commit()
        else:
            # 创建项目记录（只包含必要字段）
            project = Project(
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(project)
            db.session.commit()
        
        # 处理动态字段
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            if field_value:
                field_manager.set_field_value(project.id, field_name, field_value)
        
        flash('项目添加成功')
        
        # 获取返回URL参数，如果没有则返回列表页
        return_url = request.args.get('return_url')
        if return_url:
            return redirect(return_url)
        else:
            return redirect(url_for('project.project_list'))
    
    return render_template('project_add.html', dynamic_fields=dynamic_fields)

@project_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('project')
def project_edit(id):
    project = Project.query.get_or_404(id)
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('project')
    dynamic_fields = field_manager.get_visible_fields()
    
    if request.method == 'POST':
        print(f"开始处理项目编辑请求，项目ID: {id}")
        
        # 处理附件上传
        files = request.files.getlist('attachments')
        uploaded_files = []
        
        print(f"获取到的文件数量: {len(files)}")
        for i, file in enumerate(files):
            if file and file.filename:
                print(f"文件 {i+1}: {file.filename}")
        
        # 获取现有附件
        existing_attachments = []
        if project.attachments:
            try:
                existing_attachments = json.loads(project.attachments)
                print(f"现有附件数量: {len(existing_attachments)}")
            except Exception as e:
                print(f"解析现有附件失败: {e}")
                existing_attachments = []
        
        if files and any(f.filename for f in files):
            print("开始处理新上传的文件")
            # 获取项目名称用于创建文件夹
            project_name = ""
            for dynamic_field in dynamic_fields:
                if dynamic_field['name'] == 'name':
                    project_name = request.form.get(f'dynamic_{dynamic_field["name"]}', '')
                    break
            
            print(f"项目名称: {project_name}")
            
            # 创建项目文件夹
            if project_name:
                # 清理文件夹名称，移除特殊字符
                safe_folder_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                project_folder = os.path.join(current_app.config['PROJECT_UPLOAD_FOLDER'], safe_folder_name)
                os.makedirs(project_folder, exist_ok=True)
                print(f"创建项目文件夹: {project_folder}")
                
                # 处理每个上传的文件
                for file in files:
                    if file and file.filename:
                        # 检查文件类型
                        if not is_allowed_file(file.filename):
                            print(f"不支持的文件类型: {file.filename}")
                            flash(f'不支持的文件类型：{file.filename}，请上传PDF、Word、Excel、图片或文本文件')
                            continue
                        
                        # 生成新文件名
                        new_filename = generate_filename(project_name, file.filename)
                        upload_path = os.path.join(project_folder, new_filename)
                        print(f"保存文件: {upload_path}")
                        
                        # 保存文件
                        file.save(upload_path)
                        uploaded_files.append(os.path.join(safe_folder_name, new_filename))
            else:
                # 如果没有项目名称，使用默认路径
                for file in files:
                    if file and file.filename:
                        # 检查文件类型
                        if not is_allowed_file(file.filename):
                            print(f"不支持的文件类型: {file.filename}")
                            flash(f'不支持的文件类型：{file.filename}，请上传PDF、Word、Excel、图片或文本文件')
                            continue
                        
                        # 生成新文件名
                        new_filename = generate_filename("未命名项目", file.filename)
                        upload_path = os.path.join(current_app.config['PROJECT_UPLOAD_FOLDER'], new_filename)
                        print(f"保存文件: {upload_path}")
                        
                        # 保存文件
                        file.save(upload_path)
                        uploaded_files.append(new_filename)
            
            # 合并现有附件和新上传的附件
            all_attachments = existing_attachments + uploaded_files
            project.attachments = json.dumps(all_attachments, ensure_ascii=False)
            print(f"合并后附件数量: {len(all_attachments)}")
        else:
            # 如果没有上传新文件，保持现有附件不变
            if existing_attachments:
                project.attachments = json.dumps(existing_attachments, ensure_ascii=False)
                print(f"保持现有附件数量: {len(existing_attachments)}")
        
        print("开始保存项目信息")
        project.modified_by = current_user.username
        project.modified_at = beijing_time()
        db.session.commit()
        print("项目信息保存成功")
        
        # 处理动态字段
        print("开始处理动态字段")
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            field_manager.set_field_value(project.id, field_name, field_value)
        print("动态字段处理完成")
        
        flash('项目修改成功')
        print("项目编辑完成，准备重定向")
        
        # 获取返回URL参数，如果没有则返回列表页
        return_url = request.args.get('return_url')
        if return_url:
            return redirect(return_url)
        else:
            return redirect(url_for('project.project_list'))
    
    # 获取当前动态字段值
    current_values = {}
    for dynamic_field in dynamic_fields:
        field_value = field_manager.get_field_value(project.id, dynamic_field['name'])
        current_values[dynamic_field['name']] = field_value
    
    # 获取现有附件
    existing_attachments = []
    if project.attachments:
        try:
            existing_attachments = json.loads(project.attachments)
        except:
            existing_attachments = []
    
    return render_template('project_edit.html', 
                         project=project, 
                         dynamic_fields=dynamic_fields,
                         current_values=current_values,
                         existing_attachments=existing_attachments)

@project_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('project')
def project_delete(id):
    project = Project.query.get_or_404(id)
    
    # 删除动态字段值
    FieldValue.query.filter_by(module_name='project', record_id=id).delete()
    
    # 删除项目附件文件和文件夹
    if project.attachments:
        try:
            attachments = json.loads(project.attachments)
            for attachment in attachments:
                attachment_path = os.path.join(current_app.config['PROJECT_UPLOAD_FOLDER'], attachment)
                # 删除文件
                if os.path.isfile(attachment_path):
                    os.remove(attachment_path)
                
                # 如果附件在子文件夹中，尝试删除空文件夹
                if '/' in attachment or '\\' in attachment:
                    folder_path = os.path.dirname(attachment_path)
                    if os.path.exists(folder_path) and not os.listdir(folder_path):
                        os.rmdir(folder_path)
        except Exception:
            pass
    
    # 删除项目记录
    db.session.delete(project)
    db.session.commit()
    flash('项目删除成功')
    return redirect(url_for('project.project_list'))

@project_bp.route('/export')
@login_required
@permission_required('project')
def project_export():
    projects = Project.query.all()
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('project')
    exportable_fields = field_manager.get_exportable_fields()
    
    data = []
    for project in projects:
        row = {}
        for field in exportable_fields:
            field_value = field_manager.get_field_value(project.id, field['name'])
            row[field['label']] = field_manager.format_field_value(field_value, field)
        data.append(row)
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='项目信息导出.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@project_bp.route('/import', methods=['POST'])
@login_required
@permission_required('project')
def project_import():
    file = request.files.get('import_file')
    if not file:
        flash('请选择要导入的文件')
        return redirect(url_for('project.project_list'))
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('project')
    importable_fields = field_manager.get_importable_fields()
    
    df = pd.read_excel(file)
    for _, row in df.iterrows():
        try:
            # 创建项目记录
            project = Project(
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(project)
            db.session.commit()
            
            # 处理动态字段
            for field in importable_fields:
                field_name = field['name']
                field_label = field['label']
                field_value = row.get(field_label, '')
                if pd.notna(field_value) and field_value != '':
                    field_manager.set_field_value(project.id, field_name, str(field_value))
                    
        except Exception as e:
            print(f'导入失败: {e}, 行数据: {row.to_dict()}')
            continue
    
    flash('项目信息导入成功')
    return redirect(url_for('project.project_list'))

@project_bp.route('/template')
@login_required
@permission_required('project')
def project_template():
    # 动态字段管理器
    field_manager = DynamicFieldManager('project')
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
    return send_file(output, as_attachment=True, download_name='项目导入模板.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@project_bp.route('/download/<filename>')
@login_required
@permission_required('project')
def download_attachment(filename):
    # URL解码文件名
    filename = unquote(filename)
    
    # 检查文件是否在子文件夹中
    if '/' in filename or '\\' in filename:
        # 文件在子文件夹中
        folder_name = os.path.dirname(filename)
        file_name = os.path.basename(filename)
        folder_path = os.path.join(current_app.config['PROJECT_UPLOAD_FOLDER'], folder_name)
        return send_from_directory(folder_path, file_name)
    else:
        # 文件在根目录中
        return send_from_directory(current_app.config['PROJECT_UPLOAD_FOLDER'], filename)

@project_bp.route('/delete_attachment/<int:id>/<filename>', methods=['POST'])
@login_required
@permission_required('project')
def delete_attachment(id, filename):
    project = Project.query.get_or_404(id)
    if project.attachments:
        try:
            attachments = json.loads(project.attachments)
            if filename in attachments:
                # 删除文件
                attachment_path = os.path.join(current_app.config['PROJECT_UPLOAD_FOLDER'], filename)
                if os.path.isfile(attachment_path):
                    os.remove(attachment_path)
                
                # 如果附件在子文件夹中，尝试删除空文件夹
                if '/' in filename or '\\' in filename:
                    folder_path = os.path.dirname(attachment_path)
                    if os.path.exists(folder_path) and not os.listdir(folder_path):
                        os.rmdir(folder_path)
                
                # 从数据库中移除附件
                attachments.remove(filename)
                project.attachments = json.dumps(attachments, ensure_ascii=False)
                db.session.commit()
                flash('附件删除成功')
            else:
                flash('附件不存在')
        except Exception:
            flash('附件删除失败')
    return redirect(url_for('project.project_edit', id=id)) 