from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField
from flask import url_for, redirect, request, flash, send_file, render_template
from flask_login import current_user
from markupsafe import Markup
import os
import io
import pandas as pd
from models import Contract, Receipt, Payment, Project, Staff
from app import app, db

class ContractAdminView(ModelView):
    form_extra_fields = {
        'attachment': FileUploadField('合同附件', base_path=app.config['UPLOAD_FOLDER'], allow_overwrite=False, allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])
    }

    column_formatters = {
        'attachment': lambda v, c, m, p: Markup(
            f'<a href="{url_for("preview_attachment", filename=m.attachment)}" target="_blank">预览</a>'
            f' | <a href="{url_for("download_attachment", filename=m.attachment)}">下载</a>'
        ) if m.attachment else ''
    }

    # 搜索功能
    column_searchable_list = ['name', 'contract_number', 'party_a', 'party_b']

    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

    def on_model_delete(self, model):
        # 删除数据库记录时，删除附件文件
        if model.attachment:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], model.attachment))
            except Exception:
                pass

    # 增加导入导出按钮
    def render(self, template, **kwargs):
        if template == self.list_template:
            kwargs['export_url'] = url_for('contract_export')
            kwargs['import_url'] = url_for('contract_import')
        return super().render(template, **kwargs)

# 导出合同为Excel
@app.route('/admin/contract/export')
def contract_export():
    contracts = Contract.query.all()
    data = [
        {
            '合同名称': c.name,
            '甲方': c.party_a,
            '乙方': c.party_b,
            '合同编号': c.contract_number,
            '合同金额': c.amount,
            '签订日期': c.sign_date,
            '负责人': c.manager,
            '状态': c.status,
            '备注': c.remark
        } for c in contracts
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='合同信息.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# 导入合同Excel
@app.route('/admin/contract/import', methods=['GET', 'POST'])
def contract_import():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.xlsx'):
            flash('请上传Excel文件')
            return redirect(request.url)
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            contract = Contract(
                name=row.get('合同名称'),
                party_a=row.get('甲方'),
                party_b=row.get('乙方'),
                contract_number=row.get('合同编号'),
                amount=row.get('合同金额'),
                sign_date=row.get('签订日期'),
                manager=row.get('负责人'),
                status=row.get('状态'),
                remark=row.get('备注')
            )
            db.session.add(contract)
        db.session.commit()
        flash('导入成功')
        return redirect(url_for('contractadminview.index_view'))
    return render_template('contract_import.html')

# 收款记录
class ReceiptAdminView(ModelView):
    column_searchable_list = ['manager', 'recorder', 'amount']
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))
    def render(self, template, **kwargs):
        if template == self.list_template:
            kwargs['export_url'] = url_for('receipt_export')
            kwargs['import_url'] = url_for('receipt_import')
        return super().render(template, **kwargs)

@app.route('/admin/receipt/export')
def receipt_export():
    receipts = Receipt.query.all()
    data = [
        {
            '合同名称': r.contract.name if r.contract else '',
            '负责人': r.manager or '',
            '金额': r.amount or 0,
            '是否支付': '是' if r.is_paid else '否',
            '是否开票': '是' if r.is_invoiced else '否',
            '记录日期': r.record_date or '',
            '记录人': r.recorder or '',
            '备注': r.remark or ''
        } for r in receipts
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='收款记录.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/admin/receipt/import', methods=['GET', 'POST'])
def receipt_import():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not getattr(file, 'filename', None) or not file.filename.endswith('.xlsx'):
            flash('请上传Excel文件')
            return redirect(request.url)
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            receipt = Receipt(
                manager=row.get('负责人', ''),
                amount=row.get('金额', 0),
                is_paid=True if row.get('是否支付', '') == '是' else False,
                is_invoiced=True if row.get('是否开票', '') == '是' else False,
                record_date=row.get('记录日期', None),
                recorder=row.get('记录人', ''),
                remark=row.get('备注', '')
            )
            # 合同名称关联
            contract_name = row.get('合同名称', '')
            if contract_name:
                contract = Contract.query.filter_by(name=contract_name).first()
                if contract:
                    receipt.contract = contract
            db.session.add(receipt)
        db.session.commit()
        flash('导入成功')
        return redirect(url_for('receiptadminview.index_view'))
    return render_template('receipt_import.html')

# 付款记录
class PaymentAdminView(ModelView):
    column_searchable_list = ['manager', 'recorder', 'amount']
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))
    def render(self, template, **kwargs):
        if template == self.list_template:
            kwargs['export_url'] = url_for('payment_export')
            kwargs['import_url'] = url_for('payment_import')
        return super().render(template, **kwargs)

@app.route('/admin/payment/export')
def payment_export():
    payments = Payment.query.all()
    data = [
        {
            '合同名称': p.contract.name if p.contract else '',
            '负责人': p.manager or '',
            '金额': p.amount or 0,
            '是否支付': '是' if p.is_paid else '否',
            '是否开票': '是' if p.is_invoiced else '否',
            '记录日期': p.record_date or '',
            '记录人': p.recorder or '',
            '备注': p.remark or ''
        } for p in payments
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='付款记录.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/admin/payment/import', methods=['GET', 'POST'])
def payment_import():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not getattr(file, 'filename', None) or not file.filename.endswith('.xlsx'):
            flash('请上传Excel文件')
            return redirect(request.url)
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            payment = Payment(
                manager=row.get('负责人', ''),
                amount=row.get('金额', 0),
                is_paid=True if row.get('是否支付', '') == '是' else False,
                is_invoiced=True if row.get('是否开票', '') == '是' else False,
                record_date=row.get('记录日期', None),
                recorder=row.get('记录人', ''),
                remark=row.get('备注', '')
            )
            contract_name = row.get('合同名称', '')
            if contract_name:
                contract = Contract.query.filter_by(name=contract_name).first()
                if contract:
                    payment.contract = contract
            db.session.add(payment)
        db.session.commit()
        flash('导入成功')
        return redirect(url_for('paymentadminview.index_view'))
    return render_template('payment_import.html')

# 项目信息
class ProjectAdminView(ModelView):
    column_searchable_list = ['name', 'owner', 'contact_person', 'address']
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))
    def render(self, template, **kwargs):
        if template == self.list_template:
            kwargs['export_url'] = url_for('project_export')
            kwargs['import_url'] = url_for('project_import')
        return super().render(template, **kwargs)

@app.route('/admin/project/export')
def project_export():
    projects = Project.query.all()
    data = [
        {
            '项目名称': p.name or '',
            '业主单位': p.owner or '',
            '地址': p.address or '',
            '联系人': p.contact_person or '',
            '电话': p.contact_phone or '',
            '备注': p.remark or ''
        } for p in projects
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='项目信息.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/admin/project/import', methods=['GET', 'POST'])
def project_import():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not getattr(file, 'filename', None) or not file.filename.endswith('.xlsx'):
            flash('请上传Excel文件')
            return redirect(request.url)
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            project = Project(
                name=row.get('项目名称', ''),
                owner=row.get('业主单位', ''),
                address=row.get('地址', ''),
                contact_person=row.get('联系人', ''),
                contact_phone=row.get('电话', ''),
                remark=row.get('备注', '')
            )
            db.session.add(project)
        db.session.commit()
        flash('导入成功')
        return redirect(url_for('projectadminview.index_view'))
    return render_template('project_import.html')

# 人员信息
class StaffAdminView(ModelView):
    column_searchable_list = ['name', 'id_number', 'phone', 'bank_account']
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))
    def render(self, template, **kwargs):
        if template == self.list_template:
            kwargs['export_url'] = url_for('staff_export')
            kwargs['import_url'] = url_for('staff_import')
        return super().render(template, **kwargs)

@app.route('/admin/staff/export')
def staff_export():
    staffs = Staff.query.all()
    data = [
        {
            '姓名': s.name or '',
            '性别': s.gender or '',
            '身份证号': s.id_number or '',
            '手机号': s.phone or '',
            '银行卡号': s.bank_account or '',
            '开户行': s.bank_name or '',
            '员工类别': s.staff_type or '',
            '备注': s.remark or ''
        } for s in staffs
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='人员信息.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/admin/staff/import', methods=['GET', 'POST'])
def staff_import():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not getattr(file, 'filename', None) or not file.filename.endswith('.xlsx'):
            flash('请上传Excel文件')
            return redirect(request.url)
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            staff = Staff(
                name=row.get('姓名', ''),
                gender=row.get('性别', ''),
                id_number=row.get('身份证号', ''),
                phone=row.get('手机号', ''),
                bank_account=row.get('银行卡号', ''),
                bank_name=row.get('开户行', ''),
                staff_type=row.get('员工类别', ''),
                remark=row.get('备注', '')
            )
            db.session.add(staff)
        db.session.commit()
        flash('导入成功')
        return redirect(url_for('staffadminview.index_view'))
    return render_template('staff_import.html') 