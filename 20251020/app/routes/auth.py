from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册')
            return render_template('auth/register.html')
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('登录成功')
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误')
            
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        current_user.billing_address = request.form.get('billing_address')
        current_user.shipping_address = request.form.get('shipping_address')
        current_user.credit_card_info = request.form.get('credit_card_info')
        
        db.session.commit()
        flash('个人信息已更新')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html')