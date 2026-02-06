from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
import csv
import io
import os
from collections import defaultdict

app = Flask(__name__)

# 全局变量存储数据
participants = []  # 存储参会人员信息
seat_assignments = {}  # 存储座位分配信息


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_participants', methods=['POST'])
def upload_participants():
    global participants
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        try:
            # 读取Excel文件
            df = pd.read_excel(file, header=None, skiprows=1)
            # 只取前两列（姓名和单位）
            df = df.iloc[:, :2]
            df.columns = ['name', 'unit']
            # 过滤掉空姓名
            df = df[df['name'].notnull() & (df['name'].str.strip() != '')]
            # 转换为字典列表
            participants = df.to_dict('records')
            return jsonify({'participants': participants})
        except Exception as e:
            return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500
    else:
        return jsonify({'error': '请上传Excel文件(.xlsx或.xls)'}), 400


@app.route('/generate_seating_chart', methods=['POST'])
def generate_seating_chart():
    data = request.json
    rows = int(data.get('rows', 5))
    cols = int(data.get('cols', 6))
    aisles_input = data.get('aisles', '2,4')
    
    # 解析过道位置
    aisle_positions = []
    if aisles_input.strip() != '':
        try:
            aisle_positions = [int(pos.strip()) for pos in aisles_input.split(',') if pos.strip()]
            # 过滤有效的过道位置
            aisle_positions = [pos for pos in aisle_positions if 0 < pos <= cols]
            # 去重并排序
            aisle_positions = sorted(list(set(aisle_positions)))
        except ValueError:
            aisle_positions = []
    
    # 构建座位表数据
    seating_chart = {
        'rows': rows,
        'cols': cols,
        'aisle_positions': aisle_positions,
        'seats': []
    }
    
    # 生成座位数据
    for i in range(rows):
        row_seats = []
        col_counter = 1
        current_aisle_positions = aisle_positions.copy()
        
        for j in range(cols + len(aisle_positions)):
            is_aisle = len(current_aisle_positions) > 0 and current_aisle_positions[0] == col_counter
            
            if is_aisle:
                row_seats.append({
                    'type': 'aisle',
                    'label': '过道'
                })
                current_aisle_positions.pop(0)
            else:
                seat_id = f"{i+1}行{col_counter}列"
                seat_data = {
                    'type': 'seat',
                    'id': seat_id,
                    'row': i,
                    'col': col_counter
                }
                
                # 如果该座位已被分配
                if seat_id in seat_assignments:
                    seat_data['occupied'] = True
                    seat_data['occupant'] = seat_assignments[seat_id]
                else:
                    seat_data['occupied'] = False
                
                row_seats.append(seat_data)
                col_counter += 1
        
        seating_chart['seats'].append(row_seats)
    
    return jsonify(seating_chart)


@app.route('/assign_seat', methods=['POST'])
def assign_seat():
    global seat_assignments
    data = request.json
    seat_id = data.get('seat_id')
    participant = data.get('participant')
    
    if not seat_id or not participant:
        return jsonify({'error': '座位ID和参与者信息不能为空'}), 400
    
    seat_assignments[seat_id] = participant
    return jsonify({'success': True, 'seat_assignments': seat_assignments})


@app.route('/get_assignments', methods=['GET'])
def get_assignments():
    return jsonify(seat_assignments)


@app.route('/clear_assignments', methods=['POST'])
def clear_assignments():
    global seat_assignments
    seat_assignments = {}
    return jsonify({'success': True})


@app.route('/export_json')
def export_json():
    # 创建内存文件
    json_data = json.dumps(seat_assignments, ensure_ascii=False, indent=2)
    json_io = io.StringIO(json_data)
    json_io.seek(0)
    
    # 返回JSON文件
    return send_file(
        io.BytesIO(json_io.getvalue().encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name='座位分配.json'
    )


@app.route('/export_csv')
def export_csv():
    # 创建内存文件
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    
    # 写入表头
    writer.writerow(['座位编号', '姓名', '单位'])
    
    # 按座位编号排序
    sorted_seats = sorted(seat_assignments.keys())
    
    # 写入数据
    for seat_id in sorted_seats:
        assignment = seat_assignments[seat_id]
        writer.writerow([
            seat_id,
            assignment.get('name', ''),
            assignment.get('unit', '')
        ])
    
    # 准备下载
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='座位分配.csv'
    )


@app.route('/get_participants')
def get_participants():
    # 过滤掉已经分配座位的参与者
    assigned_names = [p['name'] for p in seat_assignments.values()]
    unassigned_participants = [p for p in participants if p['name'] not in assigned_names]
    return jsonify(unassigned_participants)


@app.route('/auto_assign_seats', methods=['POST'])
def auto_assign_seats():
    """
    自动分配座位，使同一单位的人员尽可能安排在同一列
    """
    global seat_assignments
    data = request.json
    rows = int(data.get('rows', 5))
    cols = int(data.get('cols', 6))
    aisles_input = data.get('aisles', '2,4')
    
    # 解析过道位置
    aisle_positions = []
    if aisles_input.strip() != '':
        try:
            aisle_positions = [int(pos.strip()) for pos in aisles_input.split(',') if pos.strip()]
            # 过滤有效的过道位置
            aisle_positions = [pos for pos in aisle_positions if 0 < pos <= cols]
            # 去重并排序
            aisle_positions = sorted(list(set(aisle_positions)))
        except ValueError:
            aisle_positions = []
    
    # 按单位分组参与者
    unit_groups = defaultdict(list)
    for participant in participants:
        unit = participant.get('unit', '') or '未分组'
        unit_groups[unit].append(participant)
    
    # 清空当前座位分配
    seat_assignments = {}
    
    # 计算实际座位列数（排除过道）
    actual_cols = cols
    
    # 创建座位ID列表
    seat_ids = []
    for i in range(rows):
        col_counter = 1
        current_aisle_positions = aisle_positions.copy()
        
        for j in range(cols + len(aisle_positions)):
            is_aisle = len(current_aisle_positions) > 0 and current_aisle_positions[0] == col_counter
            
            if is_aisle:
                current_aisle_positions.pop(0)
            else:
                seat_id = f"{i+1}行{col_counter}列"
                seat_ids.append(seat_id)
                col_counter += 1
    
    # 按单位人数排序，人数多的单位优先分配
    sorted_units = sorted(unit_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    # 为每个单位分配座位
    col_index = 0
    for unit, unit_participants in sorted_units:
        # 为当前单位分配座位
        for i, participant in enumerate(unit_participants):
            if col_index < len(seat_ids):
                seat_assignments[seat_ids[col_index]] = participant
                col_index += 1
    
    return jsonify({'success': True, 'seat_assignments': seat_assignments})


if __name__ == '__main__':
    app.run(debug=True)