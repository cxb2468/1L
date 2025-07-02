from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, send_file
from flask_login import login_required, current_user
from extensions import db
from models import Contract, Receipt, Payment, FieldValue
import os
from datetime import datetime, timezone, timedelta
from utils import permission_required
import pandas as pd
import io
import numpy as np
from dynamic_field_manager import DynamicFieldManager
import re
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

contract_bp = Blueprint('contract', __name__, url_prefix='/contract')

def generate_filename(contract_name, original_filename):
    """生成基于合同名称的文件名"""
    # 获取文件扩展名
    file_ext = os.path.splitext(original_filename)[1].lower()
    
    # 清理合同名称，移除特殊字符
    clean_name = re.sub(r'[^\w\s-]', '', contract_name)
    clean_name = re.sub(r'[-\s]+', '-', clean_name).strip()
    
    # 如果清理后的名称为空，使用默认名称
    if not clean_name:
        clean_name = "合同"
    
    # 添加时间戳避免重名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{clean_name}_{timestamp}{file_ext}"

def is_allowed_file(filename):
    """检查文件类型是否允许"""
    allowed_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.txt'}
    return os.path.splitext(filename)[1].lower() in allowed_extensions

@contract_bp.route('/')
@login_required
@permission_required('contract')
def contract_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '').strip()
    field = request.args.get('field', 'name')
    query = Contract.query
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('contract')
    dynamic_fields = field_manager.get_visible_fields()
    
    if q:
        # 动态字段搜索
        if field in [f['name'] for f in dynamic_fields]:
            # 在字段值表中搜索
            field_values = FieldValue.query.filter_by(
                module_name='contract',
                field_name=field
            ).filter(FieldValue.field_value.like(f'%{q}%')).all()
            record_ids = [fv.record_id for fv in field_values]
            if record_ids:
                query = query.filter(Contract.id.in_(record_ids))
            else:
                query = query.filter(Contract.id == -1)  # 无结果
    
    contracts = query.order_by(Contract.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # 为每个合同添加动态字段值
    for contract in contracts.items:
        contract.dynamic_fields = {}
        for dynamic_field in dynamic_fields:
            field_value = field_manager.get_field_value(contract.id, dynamic_field['name'])
            contract.dynamic_fields[dynamic_field['name']] = field_manager.format_field_value(field_value, dynamic_field)
    
    return render_template('contract_list.html', 
                         contracts=contracts, 
                         per_page=per_page, 
                         q=q, 
                         field=field,
                         dynamic_fields=dynamic_fields)

@contract_bp.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required('contract')
def contract_add():
    # 动态字段管理器
    field_manager = DynamicFieldManager('contract')
    dynamic_fields = field_manager.get_visible_fields()
    
    if request.method == 'POST':
        # 处理附件上传
        file = request.files.get('attachment')
        attachment = None
        if file and file.filename:
            # 检查文件类型
            if not is_allowed_file(file.filename):
                flash('不支持的文件类型，请上传PDF、Word、Excel、图片或文本文件')
                return render_template('contract_add.html', dynamic_fields=dynamic_fields)
            
            # 先创建合同记录以获取ID
            contract = Contract(
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(contract)
            db.session.commit()
            
            # 获取合同名称用于创建文件夹和文件重命名
            contract_name = ""
            for dynamic_field in dynamic_fields:
                if dynamic_field['name'] == 'name':
                    contract_name = request.form.get(f'dynamic_{dynamic_field["name"]}', '')
                    break
            
            # 处理动态字段
            for dynamic_field in dynamic_fields:
                field_name = dynamic_field['name']
                field_value = request.form.get(f'dynamic_{field_name}', '')
                if field_value:
                    field_manager.set_field_value(contract.id, field_name, field_value)
            
            # 创建合同文件夹
            if contract_name:
                # 清理文件夹名称，移除特殊字符
                safe_folder_name = "".join(c for c in contract_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                contract_folder = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], safe_folder_name)
                os.makedirs(contract_folder, exist_ok=True)
                
                # 生成新文件名
                new_filename = generate_filename(contract_name, file.filename)
                upload_path = os.path.join(contract_folder, new_filename)
                
                # 保存文件
                file.save(upload_path)
                contract.attachment = os.path.join(safe_folder_name, new_filename)
            else:
                # 如果没有合同名称，使用默认路径
                new_filename = generate_filename("未命名合同", file.filename)
                upload_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], new_filename)
                file.save(upload_path)
                contract.attachment = new_filename
            
            db.session.commit()
        else:
            # 创建合同记录（只包含必要字段）
            contract = Contract(
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(contract)
            db.session.commit()
            
            # 处理动态字段
            for dynamic_field in dynamic_fields:
                field_name = dynamic_field['name']
                field_value = request.form.get(f'dynamic_{field_name}', '')
                if field_value:
                    field_manager.set_field_value(contract.id, field_name, field_value)
        
        flash('合同添加成功')
        
        # 获取返回URL参数，如果没有则返回列表页
        return_url = request.args.get('return_url')
        if return_url:
            return redirect(return_url)
        else:
            return redirect(url_for('contract.contract_list'))
    
    return render_template('contract_add.html', dynamic_fields=dynamic_fields)

@contract_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('contract')
def contract_edit(id):
    contract = Contract.query.get_or_404(id)
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('contract')
    dynamic_fields = field_manager.get_visible_fields()
    
    if request.method == 'POST':
        # 处理附件上传
        file = request.files.get('attachment')
        if file and file.filename:
            # 检查文件类型
            if not is_allowed_file(file.filename):
                flash('不支持的文件类型，请上传PDF、Word、Excel、图片或文本文件')
                return render_template('contract_edit.html', 
                                     contract=contract, 
                                     dynamic_fields=dynamic_fields,
                                     current_values=current_values)
            
            # 删除旧附件
            if contract.attachment:
                try:
                    old_attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], contract.attachment)
                    if os.path.isfile(old_attachment_path):
                        os.remove(old_attachment_path)
                except Exception:
                    pass
            
            # 获取合同名称用于创建文件夹
            contract_name = ""
            for dynamic_field in dynamic_fields:
                if dynamic_field['name'] == 'name':
                    contract_name = request.form.get(f'dynamic_{dynamic_field["name"]}', '')
                    break
            
            # 创建合同文件夹
            if contract_name:
                # 清理文件夹名称，移除特殊字符
                safe_folder_name = "".join(c for c in contract_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                contract_folder = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], safe_folder_name)
                os.makedirs(contract_folder, exist_ok=True)
                
                # 生成新文件名
                new_filename = generate_filename(contract_name, file.filename)
                upload_path = os.path.join(contract_folder, new_filename)
                
                # 保存文件
                file.save(upload_path)
                contract.attachment = os.path.join(safe_folder_name, new_filename)
            else:
                # 如果没有合同名称，使用默认路径
                new_filename = generate_filename("未命名合同", file.filename)
                upload_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], new_filename)
                file.save(upload_path)
                contract.attachment = new_filename
        
        contract.modified_by = current_user.username
        contract.modified_at = beijing_time()
        db.session.commit()
        
        # 处理动态字段
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            field_manager.set_field_value(contract.id, field_name, field_value)
        
        flash('合同修改成功')
        
        # 获取返回URL参数，如果没有则返回列表页
        return_url = request.args.get('return_url')
        if return_url:
            return redirect(return_url)
        else:
            return redirect(url_for('contract.contract_list'))
    
    # 获取当前动态字段值
    current_values = {}
    for dynamic_field in dynamic_fields:
        field_value = field_manager.get_field_value(contract.id, dynamic_field['name'])
        current_values[dynamic_field['name']] = field_value
    
    return render_template('contract_edit.html', 
                         contract=contract, 
                         dynamic_fields=dynamic_fields,
                         current_values=current_values)

@contract_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('contract')
def contract_delete(id):
    contract = Contract.query.get_or_404(id)
    
    # 先删除相关的收付款记录的附件文件
    receipts = Receipt.query.filter_by(contract_id=id).all()
    for receipt in receipts:
        if receipt.attachment:
            try:
                attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], receipt.attachment)
                # 删除文件
                if os.path.isfile(attachment_path):
                    os.remove(attachment_path)
                
                # 如果附件在子文件夹中，尝试删除空文件夹
                if '/' in receipt.attachment or '\\' in receipt.attachment:
                    folder_path = os.path.dirname(attachment_path)
                    if os.path.exists(folder_path) and not os.listdir(folder_path):
                        os.rmdir(folder_path)
            except Exception:
                pass
    
    payments = Payment.query.filter_by(contract_id=id).all()
    for payment in payments:
        if payment.attachment:
            try:
                attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], payment.attachment)
                # 删除文件
                if os.path.isfile(attachment_path):
                    os.remove(attachment_path)
                
                # 如果附件在子文件夹中，尝试删除空文件夹
                if '/' in payment.attachment or '\\' in payment.attachment:
                    folder_path = os.path.dirname(attachment_path)
                    if os.path.exists(folder_path) and not os.listdir(folder_path):
                        os.rmdir(folder_path)
            except Exception:
                pass
    
    # 删除相关的收付款记录
    Receipt.query.filter_by(contract_id=id).delete()
    Payment.query.filter_by(contract_id=id).delete()
    
    # 删除动态字段值
    FieldValue.query.filter_by(module_name='contract', record_id=id).delete()
    
    # 删除合同附件文件和文件夹
    if contract.attachment:
        try:
            attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], contract.attachment)
            # 删除文件
            if os.path.isfile(attachment_path):
                os.remove(attachment_path)
            
            # 如果附件在子文件夹中，尝试删除空文件夹
            if '/' in contract.attachment or '\\' in contract.attachment:
                folder_path = os.path.dirname(attachment_path)
                if os.path.exists(folder_path) and not os.listdir(folder_path):
                    os.rmdir(folder_path)
        except Exception:
            pass
    
    # 删除合同记录
    db.session.delete(contract)
    db.session.commit()
    flash('合同及相关记录删除成功')
    return redirect(url_for('contract.contract_list'))

@contract_bp.route('/download/<filename>')
@login_required
@permission_required('contract')
def download_attachment(filename):
    # URL解码文件名
    filename = unquote(filename)
    
    # 检查文件是否在子文件夹中
    if '/' in filename or '\\' in filename:
        # 文件在子文件夹中
        folder_name = os.path.dirname(filename)
        file_name = os.path.basename(filename)
        folder_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], folder_name)
        return send_from_directory(folder_path, file_name)
    else:
        # 文件在根目录中
        return send_from_directory(current_app.config['CONTRACT_UPLOAD_FOLDER'], filename)

@contract_bp.route('/delete_attachment/<int:id>', methods=['POST'])
@login_required
@permission_required('contract')
def delete_attachment(id):
    contract = Contract.query.get_or_404(id)
    if contract.attachment:
        try:
            attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], contract.attachment)
            # 删除文件
            if os.path.isfile(attachment_path):
                os.remove(attachment_path)
            
            # 如果附件在子文件夹中，尝试删除空文件夹
            if '/' in contract.attachment or '\\' in contract.attachment:
                folder_path = os.path.dirname(attachment_path)
                if os.path.exists(folder_path) and not os.listdir(folder_path):
                    os.rmdir(folder_path)
            
            contract.attachment = None
            db.session.commit()
            flash('附件删除成功')
        except Exception:
            flash('附件删除失败')
    return redirect(url_for('contract.contract_list'))

# 收款跟踪
@contract_bp.route('/receipt/add/<int:contract_id>', methods=['GET', 'POST'])
@login_required
@permission_required('contract')
def receipt_add(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    field_manager = DynamicFieldManager('receipt')
    dynamic_fields = field_manager.get_visible_fields()
    return_url = request.args.get('return_url', '')
    
    if request.method == 'POST':
        return_url = request.form.get('return_url', return_url)
        # 处理附件上传
        file = request.files.get('attachment')
        attachment = None
        if file and file.filename:
            # 检查文件类型
            if not is_allowed_file(file.filename):
                flash('不支持的文件类型，请上传PDF、Word、Excel、图片或文本文件')
                return render_template('receipt_add.html', 
                                     contract=contract, 
                                     dynamic_fields=dynamic_fields,
                                     return_url=return_url)
            
            # 先创建收款记录以获取ID
            receipt = Receipt(
                contract_id=contract_id,
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(receipt)
            db.session.commit()
            
            # 获取合同名称用于创建文件夹
            contract_name = ""
            contract_field_manager = DynamicFieldManager('contract')
            contract_fields = contract_field_manager.get_visible_fields()
            for field in contract_fields:
                if field['name'] == 'name':
                    contract_name = contract_field_manager.get_field_value(contract_id, field['name'])
                    break
            
            # 获取收款记录名称用于文件重命名
            receipt_name = ""
            for dynamic_field in dynamic_fields:
                if dynamic_field['name'] == 'manager':
                    receipt_name = request.form.get(f'dynamic_{dynamic_field["name"]}', '')
                    break
            
            # 创建合同文件夹
            if contract_name:
                # 清理文件夹名称，移除特殊字符
                safe_folder_name = "".join(c for c in contract_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                contract_folder = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], safe_folder_name)
                os.makedirs(contract_folder, exist_ok=True)
                
                # 生成新文件名
                new_filename = generate_filename(f"收款_{receipt_name}", file.filename)
                upload_path = os.path.join(contract_folder, new_filename)
                
                # 保存文件
                file.save(upload_path)
                receipt.attachment = os.path.join(safe_folder_name, new_filename)
            else:
                # 如果没有合同名称，使用默认路径
                new_filename = generate_filename(f"收款_{receipt_name}", file.filename)
                upload_path = os.path.join(current_app.config['RECEIPT_UPLOAD_FOLDER'], new_filename)
                file.save(upload_path)
                receipt.attachment = new_filename
            
            db.session.commit()
        else:
            # 创建收款记录
            receipt = Receipt(
                contract_id=contract_id,
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(receipt)
            db.session.commit()
        
        # 处理动态字段
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            if field_value:
                field_manager.set_field_value(receipt.id, field_name, field_value)
        
        flash('收款记录添加成功')
        if return_url:
            return redirect(url_for('contract.receipt_list', contract_id=contract_id, return_url=return_url))
        else:
            return redirect(url_for('contract.receipt_list', contract_id=contract_id))
    
    return render_template('receipt_add.html', 
                         contract=contract, 
                         dynamic_fields=dynamic_fields,
                         return_url=return_url)

@contract_bp.route('/receipt/list/<int:contract_id>')
@login_required
@permission_required('contract')
def receipt_list(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    receipts = Receipt.query.filter_by(contract_id=contract_id).order_by(Receipt.id.desc()).all()
    field_manager = DynamicFieldManager('receipt')
    dynamic_fields = field_manager.get_visible_fields()
    for receipt in receipts:
        receipt.dynamic_fields = {}
        for dynamic_field in dynamic_fields:
            field_value = field_manager.get_field_value(receipt.id, dynamic_field['name'])
            receipt.dynamic_fields[dynamic_field['name']] = field_manager.format_field_value(field_value, dynamic_field)
    return_url = request.args.get('return_url', '')
    return render_template('receipt_list.html', 
                         contract=contract, 
                         receipts=receipts,
                         dynamic_fields=dynamic_fields,
                         return_url=return_url)

@contract_bp.route('/receipt/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('contract')
def receipt_edit(id):
    receipt = Receipt.query.get_or_404(id)
    contract = Contract.query.get_or_404(receipt.contract_id)
    field_manager = DynamicFieldManager('receipt')
    dynamic_fields = field_manager.get_visible_fields()
    return_url = request.args.get('return_url', '')
    if request.method == 'POST':
        # 处理附件上传
        file = request.files.get('attachment')
        if file and file.filename:
            # 检查文件类型
            if not is_allowed_file(file.filename):
                flash('不支持的文件类型，请上传PDF、Word、Excel、图片或文本文件')
                return render_template('receipt_edit.html', 
                                     receipt=receipt, 
                                     contract=contract,
                                     dynamic_fields=dynamic_fields,
                                     current_values=current_values,
                                     return_url=return_url)
            
            # 删除旧附件
            if receipt.attachment:
                try:
                    old_attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], receipt.attachment)
                    if os.path.isfile(old_attachment_path):
                        os.remove(old_attachment_path)
                except Exception:
                    pass
            
            # 获取合同名称用于创建文件夹
            contract_name = ""
            contract_field_manager = DynamicFieldManager('contract')
            contract_fields = contract_field_manager.get_visible_fields()
            for field in contract_fields:
                if field['name'] == 'name':
                    contract_name = contract_field_manager.get_field_value(receipt.contract_id, field['name'])
                    break
            
            # 获取收款记录名称用于文件重命名
            receipt_name = ""
            for dynamic_field in dynamic_fields:
                if dynamic_field['name'] == 'manager':
                    receipt_name = request.form.get(f'dynamic_{dynamic_field["name"]}', '')
                    break
            
            # 创建合同文件夹
            if contract_name:
                # 清理文件夹名称，移除特殊字符
                safe_folder_name = "".join(c for c in contract_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                contract_folder = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], safe_folder_name)
                os.makedirs(contract_folder, exist_ok=True)
                
                # 生成新文件名
                new_filename = generate_filename(f"收款_{receipt_name}", file.filename)
                upload_path = os.path.join(contract_folder, new_filename)
                
                # 保存文件
                file.save(upload_path)
                receipt.attachment = os.path.join(safe_folder_name, new_filename)
            else:
                # 如果没有合同名称，使用默认路径
                new_filename = generate_filename(f"收款_{receipt_name}", file.filename)
                upload_path = os.path.join(current_app.config['RECEIPT_UPLOAD_FOLDER'], new_filename)
                file.save(upload_path)
                receipt.attachment = new_filename
        
        receipt.modified_by = current_user.username
        receipt.modified_at = beijing_time()
        db.session.commit()
        
        # 处理动态字段
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            field_manager.set_field_value(receipt.id, field_name, field_value)
        
        flash('收款记录修改成功')
        if return_url:
            return redirect(url_for('contract.receipt_list', contract_id=receipt.contract_id, return_url=return_url))
        else:
            return redirect(url_for('contract.receipt_list', contract_id=receipt.contract_id))
    
    # 获取当前动态字段值
    current_values = {}
    for dynamic_field in dynamic_fields:
        field_value = field_manager.get_field_value(receipt.id, dynamic_field['name'])
        current_values[dynamic_field['name']] = field_value
    
    return render_template('receipt_edit.html', 
                         receipt=receipt, 
                         contract=contract,
                         dynamic_fields=dynamic_fields,
                         current_values=current_values,
                         return_url=return_url)

@contract_bp.route('/receipt/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('contract')
def receipt_delete(id):
    receipt = Receipt.query.get_or_404(id)
    contract_id = receipt.contract_id
    return_url = request.args.get('return_url', '')
    
    # 删除附件文件
    if receipt.attachment:
        try:
            attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], receipt.attachment)
            # 删除文件
            if os.path.isfile(attachment_path):
                os.remove(attachment_path)
            
            # 如果附件在子文件夹中，尝试删除空文件夹
            if '/' in receipt.attachment or '\\' in receipt.attachment:
                folder_path = os.path.dirname(attachment_path)
                if os.path.exists(folder_path) and not os.listdir(folder_path):
                    os.rmdir(folder_path)
        except Exception:
            pass
    
    # 删除动态字段值
    FieldValue.query.filter_by(module_name='receipt', record_id=id).delete()
    
    # 删除收款记录
    db.session.delete(receipt)
    db.session.commit()
    flash('收款记录删除成功')
    if return_url:
        return redirect(url_for('contract.receipt_list', contract_id=contract_id, return_url=return_url))
    else:
        return redirect(url_for('contract.receipt_list', contract_id=contract_id))

@contract_bp.route('/receipt/download/<filename>')
@login_required
@permission_required('contract')
def receipt_download_attachment(filename):
    # URL解码文件名
    filename = unquote(filename)
    
    # 检查文件是否在子文件夹中
    if '/' in filename or '\\' in filename:
        # 文件在子文件夹中
        folder_name = os.path.dirname(filename)
        file_name = os.path.basename(filename)
        folder_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], folder_name)
        return send_from_directory(folder_path, file_name)
    else:
        # 文件在根目录中
        return send_from_directory(current_app.config['RECEIPT_UPLOAD_FOLDER'], filename)

@contract_bp.route('/receipt/delete_attachment/<int:id>', methods=['POST'])
@login_required
@permission_required('contract')
def receipt_delete_attachment(id):
    receipt = Receipt.query.get_or_404(id)
    if receipt.attachment:
        try:
            attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], receipt.attachment)
            # 删除文件
            if os.path.isfile(attachment_path):
                os.remove(attachment_path)
            
            # 如果附件在子文件夹中，尝试删除空文件夹
            if '/' in receipt.attachment or '\\' in receipt.attachment:
                folder_path = os.path.dirname(attachment_path)
                if os.path.exists(folder_path) and not os.listdir(folder_path):
                    os.rmdir(folder_path)
            
            receipt.attachment = None
            db.session.commit()
            flash('附件删除成功')
        except Exception:
            flash('附件删除失败')
    return redirect(url_for('contract.receipt_list', contract_id=receipt.contract_id))

# 付款跟踪
@contract_bp.route('/payment/add/<int:contract_id>', methods=['GET', 'POST'])
@login_required
@permission_required('contract')
def payment_add(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    field_manager = DynamicFieldManager('payment')
    dynamic_fields = field_manager.get_visible_fields()
    return_url = request.args.get('return_url', '')
    if request.method == 'POST':
        # 处理附件上传
        file = request.files.get('attachment')
        attachment = None
        if file and file.filename:
            # 检查文件类型
            if not is_allowed_file(file.filename):
                flash('不支持的文件类型，请上传PDF、Word、Excel、图片或文本文件')
                return render_template('payment_add.html', 
                                     contract=contract, 
                                     dynamic_fields=dynamic_fields,
                                     return_url=return_url)
            
            # 先创建付款记录以获取ID
            payment = Payment(
                contract_id=contract_id,
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(payment)
            db.session.commit()
            
            # 获取合同名称用于创建文件夹
            contract_name = ""
            contract_field_manager = DynamicFieldManager('contract')
            contract_fields = contract_field_manager.get_visible_fields()
            for field in contract_fields:
                if field['name'] == 'name':
                    contract_name = contract_field_manager.get_field_value(contract_id, field['name'])
                    break
            
            # 获取付款记录名称用于文件重命名
            payment_name = ""
            for dynamic_field in dynamic_fields:
                if dynamic_field['name'] == 'manager':
                    payment_name = request.form.get(f'dynamic_{dynamic_field["name"]}', '')
                    break
            
            # 创建合同文件夹
            if contract_name:
                # 清理文件夹名称，移除特殊字符
                safe_folder_name = "".join(c for c in contract_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                contract_folder = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], safe_folder_name)
                os.makedirs(contract_folder, exist_ok=True)
                
                # 生成新文件名
                new_filename = generate_filename(f"付款_{payment_name}", file.filename)
                upload_path = os.path.join(contract_folder, new_filename)
                
                # 保存文件
                file.save(upload_path)
                payment.attachment = os.path.join(safe_folder_name, new_filename)
            else:
                # 如果没有合同名称，使用默认路径
                new_filename = generate_filename(f"付款_{payment_name}", file.filename)
                upload_path = os.path.join(current_app.config['PAYMENT_UPLOAD_FOLDER'], new_filename)
                file.save(upload_path)
                payment.attachment = new_filename
            
            db.session.commit()
        else:
            # 创建付款记录
            payment = Payment(
                contract_id=contract_id,
                modified_by=current_user.username,
                modified_at=beijing_time()
            )
            db.session.add(payment)
            db.session.commit()
        
        # 处理动态字段
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            if field_value:
                field_manager.set_field_value(payment.id, field_name, field_value)
        
        flash('付款记录添加成功')
        if return_url:
            return redirect(url_for('contract.payment_list', contract_id=contract_id, return_url=return_url))
        else:
            return redirect(url_for('contract.payment_list', contract_id=contract_id))
    return render_template('payment_add.html', 
                         contract=contract, 
                         dynamic_fields=dynamic_fields,
                         return_url=return_url)

@contract_bp.route('/payment/list/<int:contract_id>')
@login_required
@permission_required('contract')
def payment_list(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    payments = Payment.query.filter_by(contract_id=contract_id).order_by(Payment.id.desc()).all()
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('payment')
    dynamic_fields = field_manager.get_visible_fields()
    
    # 为每个付款记录添加动态字段值
    for payment in payments:
        payment.dynamic_fields = {}
        for dynamic_field in dynamic_fields:
            field_value = field_manager.get_field_value(payment.id, dynamic_field['name'])
            payment.dynamic_fields[dynamic_field['name']] = field_manager.format_field_value(field_value, dynamic_field)
    
    # 获取return_url参数
    return_url = request.args.get('return_url', '')
    return render_template('payment_list.html', 
                         contract=contract, 
                         payments=payments,
                         dynamic_fields=dynamic_fields,
                         return_url=return_url)

@contract_bp.route('/payment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('contract')
def payment_edit(id):
    payment = Payment.query.get_or_404(id)
    contract = Contract.query.get_or_404(payment.contract_id)
    field_manager = DynamicFieldManager('payment')
    dynamic_fields = field_manager.get_visible_fields()
    return_url = request.args.get('return_url', '')
    if request.method == 'POST':
        # 处理附件上传
        file = request.files.get('attachment')
        if file and file.filename:
            # 检查文件类型
            if not is_allowed_file(file.filename):
                flash('不支持的文件类型，请上传PDF、Word、Excel、图片或文本文件')
                return render_template('payment_edit.html', 
                                     payment=payment, 
                                     contract=contract,
                                     dynamic_fields=dynamic_fields,
                                     current_values=current_values,
                                     return_url=return_url)
            
            # 删除旧附件
            if payment.attachment:
                try:
                    old_attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], payment.attachment)
                    if os.path.isfile(old_attachment_path):
                        os.remove(old_attachment_path)
                except Exception:
                    pass
            
            # 获取合同名称用于创建文件夹
            contract_name = ""
            contract_field_manager = DynamicFieldManager('contract')
            contract_fields = contract_field_manager.get_visible_fields()
            for field in contract_fields:
                if field['name'] == 'name':
                    contract_name = contract_field_manager.get_field_value(payment.contract_id, field['name'])
                    break
            
            # 获取付款记录名称用于文件重命名
            payment_name = ""
            for dynamic_field in dynamic_fields:
                if dynamic_field['name'] == 'manager':
                    payment_name = request.form.get(f'dynamic_{dynamic_field["name"]}', '')
                    break
            
            # 创建合同文件夹
            if contract_name:
                # 清理文件夹名称，移除特殊字符
                safe_folder_name = "".join(c for c in contract_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                contract_folder = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], safe_folder_name)
                os.makedirs(contract_folder, exist_ok=True)
                
                # 生成新文件名
                new_filename = generate_filename(f"付款_{payment_name}", file.filename)
                upload_path = os.path.join(contract_folder, new_filename)
                
                # 保存文件
                file.save(upload_path)
                payment.attachment = os.path.join(safe_folder_name, new_filename)
            else:
                # 如果没有合同名称，使用默认路径
                new_filename = generate_filename(f"付款_{payment_name}", file.filename)
                upload_path = os.path.join(current_app.config['PAYMENT_UPLOAD_FOLDER'], new_filename)
                file.save(upload_path)
                payment.attachment = new_filename
        
        payment.modified_by = current_user.username
        payment.modified_at = beijing_time()
        db.session.commit()
        
        # 处理动态字段
        for dynamic_field in dynamic_fields:
            field_name = dynamic_field['name']
            field_value = request.form.get(f'dynamic_{field_name}', '')
            field_manager.set_field_value(payment.id, field_name, field_value)
        
        flash('付款记录修改成功')
        if return_url:
            return redirect(url_for('contract.payment_list', contract_id=payment.contract_id, return_url=return_url))
        else:
            return redirect(url_for('contract.payment_list', contract_id=payment.contract_id))
    
    # 获取当前动态字段值
    current_values = {}
    for dynamic_field in dynamic_fields:
        field_value = field_manager.get_field_value(payment.id, dynamic_field['name'])
        current_values[dynamic_field['name']] = field_value
    
    return render_template('payment_edit.html', 
                         payment=payment, 
                         contract=contract,
                         dynamic_fields=dynamic_fields,
                         current_values=current_values,
                         return_url=return_url)

@contract_bp.route('/payment/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('contract')
def payment_delete(id):
    payment = Payment.query.get_or_404(id)
    contract_id = payment.contract_id
    return_url = request.args.get('return_url', '')
    
    # 删除附件文件
    if payment.attachment:
        try:
            attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], payment.attachment)
            # 删除文件
            if os.path.isfile(attachment_path):
                os.remove(attachment_path)
            
            # 如果附件在子文件夹中，尝试删除空文件夹
            if '/' in payment.attachment or '\\' in payment.attachment:
                folder_path = os.path.dirname(attachment_path)
                if os.path.exists(folder_path) and not os.listdir(folder_path):
                    os.rmdir(folder_path)
        except Exception:
            pass
    
    # 删除动态字段值
    FieldValue.query.filter_by(module_name='payment', record_id=id).delete()
    
    # 删除付款记录
    db.session.delete(payment)
    db.session.commit()
    flash('付款记录删除成功')
    if return_url:
        return redirect(url_for('contract.payment_list', contract_id=contract_id, return_url=return_url))
    else:
        return redirect(url_for('contract.payment_list', contract_id=contract_id))

@contract_bp.route('/payment/download/<filename>')
@login_required
@permission_required('contract')
def payment_download_attachment(filename):
    # URL解码文件名
    filename = unquote(filename)
    
    # 检查文件是否在子文件夹中
    if '/' in filename or '\\' in filename:
        # 文件在子文件夹中
        folder_name = os.path.dirname(filename)
        file_name = os.path.basename(filename)
        folder_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], folder_name)
        return send_from_directory(folder_path, file_name)
    else:
        # 文件在根目录中
        return send_from_directory(current_app.config['PAYMENT_UPLOAD_FOLDER'], filename)

@contract_bp.route('/payment/delete_attachment/<int:id>', methods=['POST'])
@login_required
@permission_required('contract')
def payment_delete_attachment(id):
    payment = Payment.query.get_or_404(id)
    if payment.attachment:
        try:
            attachment_path = os.path.join(current_app.config['CONTRACT_UPLOAD_FOLDER'], payment.attachment)
            # 删除文件
            if os.path.isfile(attachment_path):
                os.remove(attachment_path)
            
            # 如果附件在子文件夹中，尝试删除空文件夹
            if '/' in payment.attachment or '\\' in payment.attachment:
                folder_path = os.path.dirname(attachment_path)
                if os.path.exists(folder_path) and not os.listdir(folder_path):
                    os.rmdir(folder_path)
            
            payment.attachment = None
            db.session.commit()
            flash('附件删除成功')
        except Exception:
            flash('附件删除失败')
    return redirect(url_for('contract.payment_list', contract_id=payment.contract_id))

@contract_bp.route('/export')
@login_required
@permission_required('contract')
def contract_export():
    contracts = Contract.query.order_by(Contract.id.desc()).all()
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('contract')
    dynamic_fields = field_manager.get_exportable_fields()
    
    # 准备导出数据
    data = []
    for contract in contracts:
        row = {
            'ID': contract.id,
            '附件': contract.attachment or '',
            '修改人': contract.modified_by or '',
            '修改时间': format_beijing_time(contract.modified_at) if contract.modified_at else ''
        }
        
        # 添加动态字段
        for field in dynamic_fields:
            field_value = field_manager.get_field_value(contract.id, field['name'])
            row[field['label']] = field_manager.format_field_value(field_value, field)
        
        data.append(row)
    
    # 创建Excel文件
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='合同列表', index=False)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'合同列表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@contract_bp.route('/import', methods=['POST'])
@login_required
@permission_required('contract')
def contract_import():
    if 'file' not in request.files:
        flash('请选择文件')
        return redirect(url_for('contract.contract_list'))
    
    file = request.files['file']
    if file.filename == '':
        flash('请选择文件')
        return redirect(url_for('contract.contract_list'))
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 动态字段管理器
        field_manager = DynamicFieldManager('contract')
        dynamic_fields = field_manager.get_importable_fields()
        
        success_count = 0
        for index, row in df.iterrows():
            try:
                # 创建合同记录
                contract = Contract(
                    modified_by=current_user.username,
                    modified_at=beijing_time()
                )
                db.session.add(contract)
                db.session.commit()
                
                # 处理动态字段
                for field in dynamic_fields:
                    field_name = field['name']
                    field_label = field['label']
                    
                    if field_label in row and pd.notna(row[field_label]):
                        field_value = str(row[field_label])
                        field_manager.set_field_value(contract.id, field_name, field_value)
                
                success_count += 1
            except Exception as e:
                print(f"导入第{index+1}行时出错: {e}")
                continue
        
        flash(f'成功导入 {success_count} 条合同记录')
    except Exception as e:
        flash(f'导入失败: {e}')
    
    return redirect(url_for('contract.contract_list'))

@contract_bp.route('/receipt/export/<int:contract_id>')
@login_required
@permission_required('contract')
def receipt_export(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    receipts = Receipt.query.filter_by(contract_id=contract_id).order_by(Receipt.id.desc()).all()
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('receipt')
    dynamic_fields = field_manager.get_exportable_fields()
    
    # 准备导出数据
    data = []
    for receipt in receipts:
        row = {
            'ID': receipt.id,
            '合同ID': receipt.contract_id,
            '修改人': receipt.modified_by or '',
            '修改时间': format_beijing_time(receipt.modified_at) if receipt.modified_at else ''
        }
        
        # 添加动态字段
        for field in dynamic_fields:
            field_value = field_manager.get_field_value(receipt.id, field['name'])
            row[field['label']] = field_manager.format_field_value(field_value, field)
        
        data.append(row)
    
    # 创建Excel文件
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='收款记录', index=False)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'收款记录_{contract.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@contract_bp.route('/receipt/import/<int:contract_id>', methods=['POST'])
@login_required
@permission_required('contract')
def receipt_import(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    
    if 'file' not in request.files:
        flash('请选择文件')
        return redirect(url_for('contract.receipt_list', contract_id=contract_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('请选择文件')
        return redirect(url_for('contract.receipt_list', contract_id=contract_id))
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 动态字段管理器
        field_manager = DynamicFieldManager('receipt')
        dynamic_fields = field_manager.get_importable_fields()
        
        success_count = 0
        for index, row in df.iterrows():
            try:
                # 创建收款记录
                receipt = Receipt(
                    contract_id=contract_id,
                    modified_by=current_user.username,
                    modified_at=beijing_time()
                )
                db.session.add(receipt)
                db.session.commit()
                
                # 处理动态字段
                for field in dynamic_fields:
                    field_name = field['name']
                    field_label = field['label']
                    
                    if field_label in row and pd.notna(row[field_label]):
                        field_value = str(row[field_label])
                        field_manager.set_field_value(receipt.id, field_name, field_value)
                
                success_count += 1
            except Exception as e:
                print(f"导入第{index+1}行时出错: {e}")
                continue
        
        flash(f'成功导入 {success_count} 条收款记录')
    except Exception as e:
        flash(f'导入失败: {e}')
    
    return redirect(url_for('contract.receipt_list', contract_id=contract_id))

@contract_bp.route('/payment/export/<int:contract_id>')
@login_required
@permission_required('contract')
def payment_export(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    payments = Payment.query.filter_by(contract_id=contract_id).order_by(Payment.id.desc()).all()
    
    # 动态字段管理器
    field_manager = DynamicFieldManager('payment')
    dynamic_fields = field_manager.get_exportable_fields()
    
    # 准备导出数据
    data = []
    for payment in payments:
        row = {
            'ID': payment.id,
            '合同ID': payment.contract_id,
            '修改人': payment.modified_by or '',
            '修改时间': format_beijing_time(payment.modified_at) if payment.modified_at else ''
        }
        
        # 添加动态字段
        for field in dynamic_fields:
            field_value = field_manager.get_field_value(payment.id, field['name'])
            row[field['label']] = field_manager.format_field_value(field_value, field)
        
        data.append(row)
    
    # 创建Excel文件
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='付款记录', index=False)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'付款记录_{contract.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@contract_bp.route('/payment/import/<int:contract_id>', methods=['POST'])
@login_required
@permission_required('contract')
def payment_import(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    
    if 'file' not in request.files:
        flash('请选择文件')
        return redirect(url_for('contract.payment_list', contract_id=contract_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('请选择文件')
        return redirect(url_for('contract.payment_list', contract_id=contract_id))
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 动态字段管理器
        field_manager = DynamicFieldManager('payment')
        dynamic_fields = field_manager.get_importable_fields()
        
        success_count = 0
        for index, row in df.iterrows():
            try:
                # 创建付款记录
                payment = Payment(
                    contract_id=contract_id,
                    modified_by=current_user.username,
                    modified_at=beijing_time()
                )
                db.session.add(payment)
                db.session.commit()
                
                # 处理动态字段
                for field in dynamic_fields:
                    field_name = field['name']
                    field_label = field['label']
                    
                    if field_label in row and pd.notna(row[field_label]):
                        field_value = str(row[field_label])
                        field_manager.set_field_value(payment.id, field_name, field_value)
                
                success_count += 1
            except Exception as e:
                print(f"导入第{index+1}行时出错: {e}")
                continue
        
        flash(f'成功导入 {success_count} 条付款记录')
    except Exception as e:
        flash(f'导入失败: {e}')
    
    return redirect(url_for('contract.payment_list', contract_id=contract_id))

@contract_bp.route('/template')
@login_required
@permission_required('contract')
def contract_template():
    # 动态字段管理器
    field_manager = DynamicFieldManager('contract')
    dynamic_fields = field_manager.get_importable_fields()
    
    # 创建模板数据
    template_data = []
    row = {}
    for field in dynamic_fields:
        row[field['label']] = ''
    template_data.append(row)
    
    # 创建Excel文件
    df = pd.DataFrame(template_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='合同导入模板', index=False)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='合同导入模板.xlsx'
    ) 