import os
import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key_for_development_only'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meeting_rooms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade="all, delete-orphan")

class MeetingRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    bookings = db.relationship('Booking', backref='room', lazy=True, cascade="all, delete-orphan")

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('meeting_room.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# 确保数据库表存在
with app.app_context():
    db.create_all()
    # 检查是否有管理员用户，如果没有则创建一个默认管理员
    if not db.session.query(User).filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
    # 如果没有会议室，添加几个示例会议室
    if not db.session.query(MeetingRoom).first():
        rooms = [
            MeetingRoom(name='主会议室', capacity=20, location='一楼大厅旁', description='配备高清投影和视频会议系统'),
            MeetingRoom(name='小会议室A', capacity=8, location='二楼东侧', description='适合小型团队讨论'),
            MeetingRoom(name='小会议室B', capacity=8, location='二楼西侧', description='适合小型团队讨论'),
            MeetingRoom(name='电话会议室', capacity=4, location='三楼东侧', description='隔音效果好，适合电话会议')
        ]
        for room in rooms:
            db.session.add(room)
        db.session.commit()

# 辅助函数
def is_admin():
    return 'user_id' in session and db.session.get(User, session['user_id']).is_admin

def get_week_dates():
    today = datetime.date.today()
    return [today + datetime.timedelta(days=i) for i in range(7)]

def format_time(dt):
    return dt.strftime('%H:%M')

def overlapping_booking(room_id, start_time, end_time, exclude_id=None):
    """检查是否有重叠的预约"""
    query = db.session.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.start_time < end_time,
        Booking.end_time > start_time
    )
    if exclude_id:
        query = query.filter(Booking.id != exclude_id)
    return query.first() is not None

def get_week_bookings():
    """获取未来7天内的会议预约"""
    now = datetime.datetime.now()
    next_week = now + datetime.timedelta(days=7)
    return db.session.query(Booking).filter(
        Booking.start_time >= now,
        Booking.start_time <= next_week
    ).order_by(Booking.start_time).all()

# 路由
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    rooms = db.session.query(MeetingRoom).all()
    dates = get_week_dates()
    
    # 准备预约数据，按会议室和日期分组
    bookings_by_room_date = {}
    for room in rooms:
        bookings_by_room_date[room.id] = {}
        for date in dates:
            start_of_day = datetime.datetime.combine(date, datetime.time.min)
            end_of_day = datetime.datetime.combine(date, datetime.time.max)
            bookings = db.session.query(Booking).filter(
                Booking.room_id == room.id,
                Booking.start_time >= start_of_day,
                Booking.end_time <= end_of_day
            ).order_by(Booking.start_time).all()
            bookings_by_room_date[room.id][date] = bookings
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .calendar { border-collapse: collapse; width: 100%; margin-bottom: 20px; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .calendar th, .calendar td { border: 1px solid #e9ecef; padding: 8px; text-align: center; }
            .calendar th { background-color: #eef2f5; color: #495057; }
            .room-name { background-color: #e6f0f7; font-weight: bold; color: #345c74; }
            .booking { margin: 3px 0; padding: 2px; border-radius: 3px; font-size: 12px; }
            .booking-mine { background-color: #e8f5e9; color: #2e7d32; }
            .booking-other { background-color: #fff3e0; color: #e65100; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-sm { padding: 4px 8px; font-size: 12px; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #495057; }
            input, select, textarea { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; background-color: white; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            .admin-section { margin-top: 30px; padding-top: 15px; border-top: 1px solid #e9ecef; }
            .login-box { max-width: 300px; margin: 50px auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px; background-color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
            .time-slot { display: inline-block; margin: 2px; padding: 2px 5px; background-color: #f0f4f8; border-radius: 3px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>会议室预约系统</h1>
            <div>
                欢迎, {{ current_user.username }}! 
                {% if is_admin %}<span style="color: #e74c3c;">[管理员]</span>{% endif %}
                <a href="{{ url_for('logout') }}" class="btn btn-sm">退出登录</a>
            </div>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            {% if is_admin %}
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
            {% endif %}
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <h2>近七日会议室预约情况</h2>
        <table class="calendar">
            <tr>
                <th>会议室</th>
                {% for date in dates %}
                <th>
                    {{ date.strftime('%m-%d') }}<br>
                    {{ ['一', '二', '三', '四', '五', '六', '日'][date.weekday()] }}
                </th>
                {% endfor %}
            </tr>
            {% for room in rooms %}
            <tr>
                <td class="room-name">
                    {{ room.name }}<br>
                    <small>({{ room.capacity }}人)</small>
                </td>
                {% for date in dates %}
                <td>
                    {% for booking in bookings_by_room_date[room.id][date] %}
                    <div class="booking {% if booking.user_id == current_user.id %}booking-mine{% else %}booking-other{% endif %}">
                        <strong>{{ booking.user.username }}</strong><br>
                        {{ format_time(booking.start_time) }}-{{ format_time(booking.end_time) }}<br>
                        <small>{{ booking.purpose[:10] }}{% if booking.purpose|length > 10 %}...{% endif %}</small>
                    </div>
                    {% else %}
                    <span style="color: #6c757d; font-size: 12px;">无预约</span>
                    {% endfor %}
                </td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    ''', 
    rooms=rooms, 
    dates=dates, 
    bookings_by_room_date=bookings_by_room_date,
    current_user=db.session.get(User, session['user_id']),
    is_admin=is_admin(),
    format_time=format_time
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 获取未来7天内的会议预约
    week_bookings = get_week_bookings()
    # 按日期分组预约
    bookings_by_date = {}
    for booking in week_bookings:
        date_str = booking.start_time.strftime('%Y-%m-%d')
        if date_str not in bookings_by_date:
            bookings_by_date[date_str] = []
        bookings_by_date[date_str].append(booking)
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(User).filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('登录成功', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>登录 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; background-color: #f8f9fa; color: #333; margin: 0; padding: 0; }
            
            /* 顶部登录区域样式 */
            .login-header { 
                background-color: white; 
                padding: 15px 20px; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                position: sticky;
                top: 0;
                z-index: 100;
            }
            .system-title { margin: 0; color: #345c74; }
            .login-form { display: flex; gap: 10px; align-items: center; }
            .login-form input { 
                padding: 8px 12px; 
                border: 1px solid #ced4da; 
                border-radius: 4px; 
                width: 150px;
            }
            .btn { 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            
            /* 预约展板区域样式 */
            .dashboard-container { 
                max-width: 1200px; 
                margin: 30px auto; 
                padding: 0 20px; 
            }
            .dashboard-header { 
                margin-bottom: 25px; 
                padding-bottom: 15px; 
                border-bottom: 2px solid #e0e6ed; 
            }
            .dashboard-title { 
                margin: 0; 
                color: #2c3e50; 
                font-size: 24px;
            }
            .dashboard-subtitle { 
                color: #6c757d; 
                margin-top: 5px;
            }
            
            /* 日期分组样式 */
            .date-section { 
                margin-bottom: 35px; 
                background-color: white; 
                border-radius: 8px; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
                overflow: hidden;
            }
            .date-header { 
                background-color: #eef2f5; 
                padding: 12px 20px; 
                border-bottom: 1px solid #e9ecef;
            }
            .date-title { 
                margin: 0; 
                color: #345c74; 
                font-size: 18px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .date-weekday { 
                color: #6c757d; 
                font-size: 16px;
                font-weight: normal;
            }
            
            /* 预约项目样式 */
            .bookings-list { 
                padding: 15px 20px; 
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
            }
            .booking-item { 
                padding: 15px; 
                border-radius: 6px; 
                background-color: #f8f9fa; 
                border-left: 3px solid #6c757d;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .booking-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 3px 5px rgba(0,0,0,0.1);
            }
            .booking-room { 
                font-weight: bold; 
                color: #345c74;
                margin-bottom: 5px;
            }
            .booking-time { 
                font-size: 0.9em; 
                color: #6c757d;
                margin-bottom: 8px;
            }
            .booking-purpose { 
                margin-top: 5px; 
                font-size: 0.9em;
                color: #333;
            }
            .booking-user {
                font-size: 0.85em;
                color: #7f8c8d;
                margin-top: 8px;
                padding-top: 8px;
                border-top: 1px dashed #e1e4e8;
            }
            
            /* 提示信息样式 */
            .alert { 
                padding: 12px 20px; 
                margin: 0 20px 20px; 
                border-radius: 4px;
                max-width: 1160px;
                margin-left: auto;
                margin-right: auto;
            }
            .alert-danger { 
                background-color: #ffebee; 
                color: #c62828; 
                border: 1px solid #ffcdd2; 
            }
            
            .no-bookings { 
                text-align: center; 
                padding: 40px 20px; 
                color: #6c757d;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
        </style>
    </head>
    <body>
        <!-- 顶部登录区域 -->
        <div class="login-header">
            <h1 class="system-title">会议室预约系统</h1>
            <form method="post" class="login-form">
                <input type="text" id="username" name="username" placeholder="用户名" required>
                <input type="password" id="password" name="password" placeholder="密码" required>
                <button type="submit" class="btn">登录</button>
            </form>
        </div>
        
        <!-- 提示信息 -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <!-- 七天预约展板 -->
        <div class="dashboard-container">
            <div class="dashboard-header">
                <h2 class="dashboard-title">近七日会议预约安排</h2>
                <p class="dashboard-subtitle">展示未来7天内所有会议室的预约情况</p>
            </div>
            
            {% if bookings_by_date %}
                {% for date_str, bookings in bookings_by_date.items() %}
                <div class="date-section">
                    <div class="date-header">
                        <h3 class="date-title">
                            {{ date_str }}
                            <span class="date-weekday">
                                {{ ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][datetime.datetime.strptime(date_str, '%Y-%m-%d').weekday()] }}
                            </span>
                        </h3>
                    </div>
                    <div class="bookings-list">
                        {% for booking in bookings %}
                        <div class="booking-item">
                            <div class="booking-room">{{ booking.room.name }} ({{ booking.room.location }})</div>
                            <div class="booking-time">
                                {{ booking.start_time.strftime('%H:%M') }} - {{ booking.end_time.strftime('%H:%M') }}
                            </div>
                            <div class="booking-purpose">{{ booking.purpose }}</div>
                            <div class="booking-user">预约人: {{ booking.user.username }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-bookings">
                    未来7天内暂无会议预约
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    ''', 
    bookings_by_date=bookings_by_date,
    datetime=datetime
    )

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录', 'success')
    return redirect(url_for('login'))

# 密码修改功能（适用于所有用户）
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = db.session.get(User, session['user_id'])
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # 验证当前密码
        if not check_password_hash(current_user.password_hash, current_password):
            flash('当前密码不正确', 'danger')
            return redirect(url_for('change_password'))
        
        # 验证新密码
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'danger')
            return redirect(url_for('change_password'))
        
        # 确保新密码不为空
        if not new_password:
            flash('新密码不能为空', 'danger')
            return redirect(url_for('change_password'))
        
        # 更新密码
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('密码已成功更新，请使用新密码登录', 'success')
        return redirect(url_for('logout'))  # 密码修改后强制重新登录
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>修改密码 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #495057; }
            input { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; }
            .form-container { margin-top: 20px; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px; background-color: white; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>修改密码</h1>
            <a href="{{ url_for('index') }}" class="btn btn-sm">返回首页</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            {% if is_admin %}
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
            {% endif %}
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="form-container">
            <form method="post">
                <div class="form-group">
                    <label for="current_password">当前密码</label>
                    <input type="password" id="current_password" name="current_password" required>
                </div>
                
                <div class="form-group">
                    <label for="new_password">新密码</label>
                    <input type="password" id="new_password" name="new_password" required>
                </div>
                
                <div class="form-group">
                    <label for="confirm_password">确认新密码</label>
                    <input type="password" id="confirm_password" name="confirm_password" required>
                </div>
                
                <button type="submit" class="btn">确认修改</button>
                <a href="{{ url_for('index') }}" class="btn btn-danger">取消</a>
            </form>
        </div>
    </body>
    </html>
    ''', current_user=current_user, is_admin=is_admin())

@app.route('/book', methods=['GET', 'POST'])
def book_room():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    rooms = db.session.query(MeetingRoom).all()
    
    if request.method == 'POST':
        room_id = int(request.form['room_id'])
        date_str = request.form['date']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        purpose = request.form['purpose']
        
        # 解析日期时间
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
            
            start_datetime = datetime.datetime.combine(date, start_time)
            end_datetime = datetime.datetime.combine(date, end_time)
            
            # 验证时间
            if start_datetime >= end_datetime:
                flash('结束时间必须晚于开始时间', 'danger')
                return redirect(url_for('book_room'))
                
            today = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            if start_datetime < today:
                flash('不能预约过去的时间', 'danger')
                return redirect(url_for('book_room'))
                
            # 检查是否超过7天
            if start_datetime > today + datetime.timedelta(days=7):
                flash('最多只能预约7天内的会议室', 'danger')
                return redirect(url_for('book_room'))
                
            # 检查是否有重叠预约
            if overlapping_booking(room_id, start_datetime, end_datetime):
                flash('该时间段已有预约，请选择其他时间', 'danger')
                return redirect(url_for('book_room'))
                
            # 创建预约
            booking = Booking(
                user_id=session['user_id'],
                room_id=room_id,
                start_time=start_datetime,
                end_time=end_datetime,
                purpose=purpose
            )
            db.session.add(booking)
            db.session.commit()
            
            flash('预约成功', 'success')
            return redirect(url_for('index'))
            
        except ValueError:
            flash('日期或时间格式错误', 'danger')
            return redirect(url_for('book_room'))
    
    # 生成时间段选项（每30分钟一个）
    time_slots = []
    for hour in range(8, 22):  # 8:00 - 21:30
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            time_slots.append(time_str)
    
    # 生成未来7天的日期选项
    dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(8)]
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>预约会议室 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #495057; }
            input, select, textarea { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>预约会议室</h1>
            <a href="{{ url_for('index') }}" class="btn btn-sm">返回首页</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            {% if is_admin %}
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
            {% endif %}
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="post">
            <div class="form-group">
                <label for="room_id">选择会议室</label>
                <select id="room_id" name="room_id" required>
                    {% for room in rooms %}
                    <option value="{{ room.id }}">{{ room.name }} ({{ room.capacity }}人, {{ room.location }})</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="date">选择日期</label>
                <input type="date" id="date" name="date" required>
            </div>
            
            <div class="form-group">
                <label for="start_time">开始时间</label>
                <select id="start_time" name="start_time" required>
                    {% for time in time_slots %}
                    <option value="{{ time }}">{{ time }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="end_time">结束时间</label>
                <select id="end_time" name="end_time" required>
                    {% for time in time_slots %}
                    <option value="{{ time }}">{{ time }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="purpose">会议内容（必填项：1、会议内容，2、是否计划内会议。可填项：是否需要视频会议、投影、麦克风、横幅及内容、桌牌等）</label>
                <textarea id="purpose" name="purpose" rows="3" required></textarea>
            </div>
            
            <button type="submit" class="btn">确认预约</button>
            <a href="{{ url_for('index') }}" class="btn btn-danger">取消</a>
        </form>
    </body>
    </html>
    ''', 
    rooms=rooms, 
    time_slots=time_slots,
    dates=dates,
    is_admin=is_admin()
    )

@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取当前用户的所有预约，按时间倒序排列
    bookings = db.session.query(Booking).filter_by(user_id=session['user_id']).order_by(Booking.start_time.desc()).all()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>我的预约 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-sm { padding: 4px 8px; font-size: 12px; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            th, td { border: 1px solid #e9ecef; padding: 10px; text-align: left; }
            th { background-color: #eef2f5; color: #495057; }
            tr:nth-child(even) { background-color: #f8f9fa; }
            .actions { display: flex; gap: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>我的预约</h1>
            <a href="{{ url_for('index') }}" class="btn btn-sm">返回首页</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            {% if is_admin %}
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
            {% endif %}
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <a href="{{ url_for('book_room') }}" class="btn">新增预约</a>
        
        {% if bookings %}
        <table>
            <tr>
                <th>会议室</th>
                <th>日期</th>
                <th>时间</th>
                <th>会议内容</th>
                <th>状态</th>
                <th>操作</th>
            </tr>
            {% for booking in bookings %}
            <tr>
                <td>{{ booking.room.name }}</td>
                <td>{{ booking.start_time.strftime('%Y-%m-%d') }}</td>
                <td>{{ booking.start_time.strftime('%H:%M') }} - {{ booking.end_time.strftime('%H:%M') }}</td>
                <td>{{ booking.purpose }}</td>
                <td>
                    {% if booking.end_time < datetime.datetime.now() %}
                    <span style="color: #999;">已结束</span>
                    {% else %}
                    <span style="color: #2e7d32;">进行中</span>
                    {% endif %}
                </td>
                <td class="actions">
                    {% if booking.start_time > datetime.datetime.now() %}
                    <a href="{{ url_for('edit_booking', booking_id=booking.id) }}" class="btn btn-sm">编辑</a>
                    <a href="{{ url_for('delete_booking', booking_id=booking.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('确定要删除这个预约吗？')">删除</a>
                    {% else %}
                    <span style="color: #999;">不可修改</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p style="margin-top: 20px;">您暂无任何预约</p>
        {% endif %}
    </body>
    </html>
    ''', 
    bookings=bookings,
    is_admin=is_admin(),
    datetime=datetime
    )

@app.route('/edit-booking/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    booking = db.session.get(Booking, booking_id)
    
    # 检查权限：只能编辑自己的预约，且预约尚未开始
    if booking.user_id != session['user_id'] and not is_admin():
        flash('没有权限编辑此预约', 'danger')
        return redirect(url_for('my_bookings'))
    
    if booking.start_time < datetime.datetime.now():
        flash('不能编辑已开始或已结束的预约', 'danger')
        return redirect(url_for('my_bookings'))
    
    rooms = db.session.query(MeetingRoom).all()
    
    if request.method == 'POST':
        room_id = int(request.form['room_id'])
        date_str = request.form['date']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        purpose = request.form['purpose']
        
        # 解析日期时间
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
            
            start_datetime = datetime.datetime.combine(date, start_time)
            end_datetime = datetime.datetime.combine(date, end_time)
            
            # 验证时间
            if start_datetime >= end_datetime:
                flash('结束时间必须晚于开始时间', 'danger')
                return redirect(url_for('edit_booking', booking_id=booking_id))
                
            today = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            if start_datetime < today:
                flash('不能预约过去的时间', 'danger')
                return redirect(url_for('edit_booking', booking_id=booking_id))
                
            # 检查是否超过7天
            if start_datetime > today + datetime.timedelta(days=7):
                flash('最多只能预约7天内的会议室', 'danger')
                return redirect(url_for('edit_booking', booking_id=booking_id))
                
            # 检查是否有重叠预约（排除当前预约）
            if overlapping_booking(room_id, start_datetime, end_datetime, exclude_id=booking_id):
                flash('该时间段已有预约，请选择其他时间', 'danger')
                return redirect(url_for('edit_booking', booking_id=booking_id))
                
            # 更新预约
            booking.room_id = room_id
            booking.start_time = start_datetime
            booking.end_time = end_datetime
            booking.purpose = purpose
            
            db.session.commit()
            
            flash('预约已更新', 'success')
            return redirect(url_for('my_bookings'))
            
        except ValueError:
            flash('日期或时间格式错误', 'danger')
            return redirect(url_for('edit_booking', booking_id=booking_id))
    
    # 生成时间段选项（每30分钟一个）
    time_slots = []
    for hour in range(8, 22):  # 8:00 - 21:30
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            time_slots.append(time_str)
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>编辑预约 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #495057; }
            input, select, textarea { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>编辑预约</h1>
            <a href="{{ url_for('my_bookings') }}" class="btn btn-sm">返回我的预约</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            {% if is_admin %}
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
            {% endif %}
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="post">
            <div class="form-group">
                <label for="room_id">选择会议室</label>
                <select id="room_id" name="room_id" required>
                    {% for room in rooms %}
                    <option value="{{ room.id }}" {% if room.id == booking.room_id %}selected{% endif %}>
                        {{ room.name }} ({{ room.capacity }}人, {{ room.location }})
                    </option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="date">选择日期</label>
                <input type="date" id="date" name="date" value="{{ booking.start_time.strftime('%Y-%m-%d') }}" required>
            </div>
            
            <div class="form-group">
                <label for="start_time">开始时间</label>
                <select id="start_time" name="start_time" required>
                    {% for time in time_slots %}
                    <option value="{{ time }}" {% if time == booking.start_time.strftime('%H:%M') %}selected{% endif %}>{{ time }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="end_time">结束时间</label>
                <select id="end_time" name="end_time" required>
                    {% for time in time_slots %}
                    <option value="{{ time }}" {% if time == booking.end_time.strftime('%H:%M') %}selected{% endif %}>{{ time }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="purpose">会议内容（必填项：1、会议内容，2、是否计划内会议。可填项：是否需要视频会议、投影、麦克风、横幅及内容、桌牌等）</label>
                <textarea id="purpose" name="purpose" rows="3" required>{{ booking.purpose }}</textarea>
            </div>
            
            <button type="submit" class="btn">保存修改</button>
            <a href="{{ url_for('my_bookings') }}" class="btn btn-danger">取消</a>
        </form>
    </body>
    </html>
    ''', 
    booking=booking,
    rooms=rooms, 
    time_slots=time_slots,
    is_admin=is_admin()
    )

@app.route('/delete-booking/<int:booking_id>')
def delete_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    booking = db.session.get(Booking, booking_id)
    
    # 检查权限：只能删除自己的预约，且预约尚未开始
    if booking.user_id != session['user_id'] and not is_admin():
        flash('没有权限删除此预约', 'danger')
        return redirect(url_for('my_bookings'))
    
    if booking.start_time < datetime.datetime.now() and not is_admin():
        flash('不能删除已开始或已结束的预约', 'danger')
        return redirect(url_for('my_bookings'))
    
    db.session.delete(booking)
    db.session.commit()
    
    flash('预约已删除', 'success')
    return redirect(url_for('my_bookings'))

# 管理员路由 - 添加新用户
@app.route('/admin/add-user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        # 将变量名改为user_is_admin，避免与全局函数名冲突
        user_is_admin = 'is_admin' in request.form
        
        # 验证密码
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('add_user'))
        
        # 检查用户名是否已存在
        if db.session.query(User).filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('add_user'))
        
        # 创建新用户
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=user_is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'用户 {username} 创建成功', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>添加新用户 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #495057; }
            input { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>添加新用户</h1>
            <a href="{{ url_for('admin_users') }}" class="btn btn-sm">返回用户列表</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="post">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="form-group">
                <label for="confirm_password">确认密码</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="is_admin"> 
                    授予管理员权限
                </label>
            </div>
            
            <button type="submit" class="btn">创建用户</button>
            <a href="{{ url_for('admin_users') }}" class="btn btn-danger">取消</a>
        </form>
    </body>
    </html>
    ''', is_admin=is_admin())

# 管理员路由 - 用户管理
@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    users = db.session.query(User).all()
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>管理用户 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-sm { padding: 4px 8px; font-size: 12px; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            th, td { border: 1px solid #e9ecef; padding: 10px; text-align: left; }
            th { background-color: #eef2f5; color: #495057; }
            tr:nth-child(even) { background-color: #f8f9fa; }
            .actions { display: flex; gap: 5px; }
            .admin-badge { display: inline-block; padding: 2px 5px; background-color: #ffebee; color: #c62828; border-radius: 3px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>管理用户</h1>
            <a href="{{ url_for('index') }}" class="btn btn-sm">返回首页</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <a href="{{ url_for('add_user') }}" class="btn">添加新用户</a>
        
        <h2>用户列表</h2>
        {% if users %}
        <table>
            <tr>
                <th>用户名</th>
                <th>角色</th>
                <th>操作</th>
            </tr>
            {% for user in users %}
            <tr>
                <td>{{ user.username }}</td>
                <td>{% if user.is_admin %}<span class="admin-badge">管理员</span>{% else %}普通用户{% endif %}</td>
                <td class="actions">
                    {% if user.username != 'admin' %} {# 保护默认管理员不被删除 #}
                    <a href="{{ url_for('edit_user', user_id=user.id) }}" class="btn btn-sm">编辑</a>
                    <a href="{{ url_for('reset_password', user_id=user.id) }}" class="btn btn-sm" style="background-color: #3498db;" onclick="return confirm('确定要重置用户 {{ user.username }} 的密码吗？密码将被设置为 Brcb123!@#')">重置密码</a>
                    <a href="{{ url_for('delete_user', user_id=user.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('确定要删除用户 {{ user.username }} 吗？该用户的所有预约也将被删除！')">删除</a>
                    {% else %}
                    <span style="color: #999;">系统管理员</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>暂无用户</p>
        {% endif %}
    </body>
    </html>
    ''', users=users, is_admin=is_admin())

# 管理员重置用户密码功能
@app.route('/admin/reset-password/<int:user_id>')
def reset_password(user_id):
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    user = db.session.get(User, user_id)
    
    # 保护默认管理员不被修改密码
    if user.username == 'admin':
        flash('不能重置系统管理员账号密码', 'danger')
        return redirect(url_for('admin_users'))
    
    # 重置密码为固定值 Brcb123!@#
    user.password_hash = generate_password_hash('Brcb123!@#')
    db.session.commit()
    
    flash(f'用户 {user.username} 的密码已重置为 Brcb123!@#', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    user = db.session.get(User, user_id)
    
    # 保护默认管理员不被修改
    if user.username == 'admin':
        flash('不能修改系统管理员账号', 'danger')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        # 处理用户名变更
        new_username = request.form['username']
        if new_username != user.username:
            if db.session.query(User).filter_by(username=new_username).first():
                flash('用户名已存在', 'danger')
                return redirect(url_for('edit_user', user_id=user_id))
            user.username = new_username
        
        # 处理管理员权限变更
        user.is_admin = 'is_admin' in request.form
        
        # 处理密码变更（如果提供了新密码）
        new_password = request.form['new_password']
        if new_password:
            confirm_password = request.form['confirm_password']
            if new_password != confirm_password:
                flash('两次输入的密码不一致', 'danger')
                return redirect(url_for('edit_user', user_id=user_id))
            user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>编辑用户 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #495057; }
            input, textarea { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; }
            .form-section { margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
            .form-section h3 { margin-top: 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>编辑用户</h1>
            <a href="{{ url_for('admin_users') }}" class="btn btn-sm">返回用户列表</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="post">
            <div class="form-section">
                <h3>基本信息</h3>
                <div class="form-group">
                    <label for="username">用户名</label>
                    <input type="text" id="username" name="username" value="{{ user.username }}" required>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="is_admin" {% if user.is_admin %}checked{% endif %}> 
                        授予管理员权限
                    </label>
                </div>
            </div>
            
            <div class="form-section">
                <h3>密码修改（可选）</h3>
                <p>如果不需要修改密码，请留空</p>
                <div class="form-group">
                    <label for="new_password">新密码</label>
                    <input type="password" id="new_password" name="new_password">
                </div>
                
                <div class="form-group">
                    <label for="confirm_password">确认新密码</label>
                    <input type="password" id="confirm_password" name="confirm_password">
                </div>
            </div>
            
            <button type="submit" class="btn">保存修改</button>
            <a href="{{ url_for('admin_users') }}" class="btn btn-danger">取消</a>
        </form>
    </body>
    </html>
    ''', user=user, is_admin=is_admin())

@app.route('/admin/delete-user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    user = db.session.get(User, user_id)
    
    # 保护默认管理员不被删除
    if user.username == 'admin':
        flash('不能删除系统管理员账号', 'danger')
        return redirect(url_for('admin_users'))
    
    # 如果当前登录用户是被删除的用户，先退出登录
    if session.get('user_id') == user_id:
        session.pop('user_id', None)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'用户 {user.username} 已删除，相关预约也已清除', 'success')
    return redirect(url_for('admin_users'))

# 管理员路由 - 会议室管理
@app.route('/admin/rooms', methods=['GET', 'POST'])
def admin_rooms():
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        capacity = int(request.form['capacity'])
        location = request.form['location']
        description = request.form['description']
        
        # 检查会议室名称是否已存在
        if db.session.query(MeetingRoom).filter_by(name=name).first():
            flash('会议室名称已存在', 'danger')
            return redirect(url_for('admin_rooms'))
        
        room = MeetingRoom(
            name=name,
            capacity=capacity,
            location=location,
            description=description
        )
        db.session.add(room)
        db.session.commit()
        
        flash('会议室添加成功', 'success')
        return redirect(url_for('admin_rooms'))
    
    rooms = db.session.query(MeetingRoom).all()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>管理会议室 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-sm { padding: 4px 8px; font-size: 12px; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            th, td { border: 1px solid #e9ecef; padding: 10px; text-align: left; }
            th { background-color: #eef2f5; color: #495057; }
            tr:nth-child(even) { background-color: #f8f9fa; }
            .actions { display: flex; gap: 5px; }
            .form-container { margin-top: 30px; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px; background-color: white; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #495057; }
            input, textarea { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>管理会议室</h1>
            <a href="{{ url_for('index') }}" class="btn btn-sm">返回首页</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <h2>会议室列表</h2>
        {% if rooms %}
        <table>
            <tr>
                <th>名称</th>
                <th>容量</th>
                <th>位置</th>
                <th>描述</th>
                <th>操作</th>
            </tr>
            {% for room in rooms %}
            <tr>
                <td>{{ room.name }}</td>
                <td>{{ room.capacity }}人</td>
                <td>{{ room.location }}</td>
                <td>{{ room.description }}</td>
                <td class="actions">
                    <a href="{{ url_for('edit_room', room_id=room.id) }}" class="btn btn-sm">编辑</a>
                    <a href="{{ url_for('delete_room', room_id=room.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('确定要删除这个会议室吗？相关预约也会被删除！')">删除</a>
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>暂无会议室，请添加会议室</p>
        {% endif %}
        
        <div class="form-container">
            <h2>添加新会议室</h2>
            <form method="post">
                <div class="form-group">
                    <label for="name">会议室名称</label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div class="form-group">
                    <label for="capacity">容纳人数</label>
                    <input type="number" id="capacity" name="capacity" min="1" required>
                </div>
                
                <div class="form-group">
                    <label for="location">位置</label>
                    <input type="text" id="location" name="location" required>
                </div>
                
                <div class="form-group">
                    <label for="description">描述</label>
                    <textarea id="description" name="description" rows="3"></textarea>
                </div>
                
                <button type="submit" class="btn">添加会议室</button>
            </form>
        </div>
    </body>
    </html>
    ''', rooms=rooms, is_admin=is_admin())

@app.route('/admin/edit-room/<int:room_id>', methods=['GET', 'POST'])
def edit_room(room_id):
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    room = db.session.get(MeetingRoom, room_id)
    
    if request.method == 'POST':
        name = request.form['name']
        capacity = int(request.form['capacity'])
        location = request.form['location']
        description = request.form['description']
        
        # 检查会议室名称是否已存在（排除当前会议室）
        existing_room = db.session.query(MeetingRoom).filter_by(name=name).first()
        if existing_room and existing_room.id != room_id:
            flash('会议室名称已存在', 'danger')
            return redirect(url_for('edit_room', room_id=room_id))
        
        room.name = name
        room.capacity = capacity
        room.location = location
        room.description = description
        
        db.session.commit()
        
        flash('会议室信息已更新', 'success')
        return redirect(url_for('admin_rooms'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>编辑会议室 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            .btn:hover { background-color: #5a6268; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #495057; }
            input, textarea { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>编辑会议室</h1>
            <a href="{{ url_for('admin_rooms') }}" class="btn btn-sm">返回会议室列表</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="post">
            <div class="form-group">
                <label for="name">会议室名称</label>
                <input type="text" id="name" name="name" value="{{ room.name }}" required>
            </div>
            
            <div class="form-group">
                <label for="capacity">容纳人数</label>
                <input type="number" id="capacity" name="capacity" min="1" value="{{ room.capacity }}" required>
            </div>
            
            <div class="form-group">
                <label for="location">位置</label>
                <input type="text" id="location" name="location" value="{{ room.location }}" required>
            </div>
            
            <div class="form-group">
                <label for="description">描述</label>
                <textarea id="description" name="description" rows="3">{{ room.description }}</textarea>
            </div>
            
            <button type="submit" class="btn">保存修改</button>
            <a href="{{ url_for('admin_rooms') }}" class="btn btn-danger">取消</a>
        </form>
    </body>
    </html>
    ''', room=room, is_admin=is_admin())

@app.route('/admin/delete-room/<int:room_id>')
def delete_room(room_id):
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    room = db.session.get(MeetingRoom, room_id)
    
    # 删除该会议室的所有预约
    bookings = db.session.query(Booking).filter_by(room_id=room_id).all()
    for booking in bookings:
        db.session.delete(booking)
    
    # 删除会议室
    db.session.delete(room)
    db.session.commit()
    
    flash('会议室已删除，相关预约也已清除', 'success')
    return redirect(url_for('admin_rooms'))

@app.route('/admin/bookings')
def admin_bookings():
    if 'user_id' not in session or not is_admin():
        return redirect(url_for('login'))
    
    # 获取所有预约，按时间倒序排列
    bookings = db.session.query(Booking).order_by(Booking.start_time.desc()).all()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>管理所有预约 - 会议室预约系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; color: #333; }
            .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef; }
            .nav { margin-bottom: 20px; padding: 10px 0; background-color: #eef2f5; border-radius: 6px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #495057; padding: 8px 12px; border-radius: 4px; transition: background-color 0.3s; }
            .nav a:hover { text-decoration: none; background-color: #dce4eb; }
            .btn { 
                display: inline-block; 
                padding: 8px 16px; 
                background-color: #6c757d; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                font-size: 14px;
                transition: background-color 0.3s; 
            }
            .btn:hover { background-color: #5a6268; }
            .btn-sm { padding: 4px 8px; font-size: 12px; }
            .btn-danger { background-color: #e74c3c; }
            .btn-danger:hover { background-color: #c0392b; }
            .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
            .alert-success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
            .alert-danger { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            th, td { border: 1px solid #e9ecef; padding: 10px; text-align: left; }
            th { background-color: #eef2f5; color: #495057; }
            tr:nth-child(even) { background-color: #f8f9fa; }
            .actions { display: flex; gap: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>管理所有预约</h1>
            <a href="{{ url_for('index') }}" class="btn btn-sm">返回首页</a>
        </div>
        
        <div class="nav">
            <a href="{{ url_for('index') }}">首页</a>
            <a href="{{ url_for('book_room') }}">预约会议室</a>
            <a href="{{ url_for('my_bookings') }}">我的预约</a>
            <a href="{{ url_for('change_password') }}">修改密码</a>
            <a href="{{ url_for('admin_rooms') }}">管理会议室</a>
            <a href="{{ url_for('admin_bookings') }}">管理所有预约</a>
            <a href="{{ url_for('admin_users') }}">管理用户</a>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% if bookings %}
        <table>
            <tr>
                <th>用户</th>
                <th>会议室</th>
                <th>日期</th>
                <th>时间</th>
                <th>会议内容</th>
                <th>状态</th>
                <th>操作</th>
            </tr>
            {% for booking in bookings %}
            <tr>
                <td>{{ booking.user.username }}</td>
                <td>{{ booking.room.name }}</td>
                <td>{{ booking.start_time.strftime('%Y-%m-%d') }}</td>
                <td>{{ booking.start_time.strftime('%H:%M') }} - {{ booking.end_time.strftime('%H:%M') }}</td>
                <td>{{ booking.purpose }}</td>
                <td>
                    {% if booking.end_time < datetime.datetime.now() %}
                    <span style="color: #999;">已结束</span>
                    {% else %}
                    <span style="color: #2e7d32;">进行中</span>
                    {% endif %}
                </td>
                <td class="actions">
                    <a href="{{ url_for('edit_booking', booking_id=booking.id) }}" class="btn btn-sm">编辑</a>
                    <a href="{{ url_for('delete_booking', booking_id=booking.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('确定要删除这个预约吗？')">删除</a>
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>暂无任何预约</p>
        {% endif %}
    </body>
    </html>
    ''', 
    bookings=bookings,
    datetime=datetime,
    is_admin=is_admin()
    )

if __name__ == '__main__':
    # 获取本地IP地址
    import socket
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
    
    local_ip = get_local_ip()
    print(f"会议室预约系统已启动，局域网访问地址: http://{local_ip}:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
    