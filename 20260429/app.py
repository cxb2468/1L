# Flask Web应用 - 农历生日转换器
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import sys
from datetime import datetime
import tempfile
import pandas as pd

# 导入生日转换模块
from birthday_converter import process_excel_file_by_year

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# 创建必要的文件夹
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """首页"""
    current_year = datetime.now().year
    return render_template('index.html', current_year=current_year)


@app.route('/convert', methods=['POST'])
def convert_birthday():
    """处理生日转换请求"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('不支持的文件格式，请上传Excel文件(.xlsx或.xls)', 'error')
            return redirect(url_for('index'))
        
        # 获取目标年份
        target_year = request.form.get('year', type=int)
        if not target_year:
            flash('请输入有效的年份', 'error')
            return redirect(url_for('index'))
        
        if target_year < 1900 or target_year > 2100:
            flash('年份超出范围（1900-2100）', 'error')
            return redirect(url_for('index'))
        
        # 是否按月拆分
        split_by_month = request.form.get('split_month') == 'on'
        
        # 保存上传的文件
        filename = file.filename
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # 生成输出文件名
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_{target_year}年公历生日.xlsx"
        download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
        
        # 处理Excel文件
        print(f"\n开始处理文件: {filename}")
        print(f"目标年份: {target_year}")
        print(f"按月拆分: {split_by_month}")
        
        process_excel_file_by_year(
            input_file=upload_path,
            target_year=target_year,
            output_file=download_path,
            split_by_month=split_by_month
        )
        
        # 清理上传文件
        if os.path.exists(upload_path):
            os.remove(upload_path)
        
        flash(f'转换成功！目标年份: {target_year}', 'success')
        
        # 发送文件给客户端下载
        return send_file(
            download_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"处理出错: {e}")
        import traceback
        traceback.print_exc()
        flash(f'处理失败: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/cleanup')
def cleanup():
    """清理临时文件（可选的管理功能）"""
    try:
        # 清理上传文件夹
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # 清理下载文件夹（保留最近1小时的文件）
        import time
        current_time = time.time()
        for filename in os.listdir(app.config['DOWNLOAD_FOLDER']):
            file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 3600:  # 超过1小时
                    os.remove(file_path)
        
        flash('临时文件清理完成', 'success')
    except Exception as e:
        flash(f'清理失败: {str(e)}', 'error')
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("="*60)
    print("农历生日转换器 - Web版")
    print("="*60)
    print(f"访问地址: http://localhost:5001")
    print(f"按 Ctrl+C 停止服务器")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5001)
