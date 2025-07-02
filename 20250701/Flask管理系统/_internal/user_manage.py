from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager
from models import User

user_bp = Blueprint('user', __name__, url_prefix='/user')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@user_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.is_admin:
        flash('无权限')
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        permissions = request.form.getlist('permissions')
        permissions_str = ','.join(permissions)
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
        else:
            user = User(username=username, password=generate_password_hash(password), is_admin=is_admin, permissions=permissions_str)
            db.session.add(user)
            db.session.commit()
            flash('用户创建成功')
            return redirect(url_for('user.user_list'))
    return render_template('register.html')

@user_bp.route('/list')
@login_required
def user_list():
    if not current_user.is_admin:
        flash('无权限')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('user_list.html', users=users)

@user_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not current_user.is_admin:
        flash('无权限')
        return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        password = request.form['password']
        if password:
            user.password = generate_password_hash(password)
        user.is_admin = 'is_admin' in request.form
        permissions = request.form.getlist('permissions')
        user.permissions = ','.join(permissions)
        db.session.commit()
        flash('用户信息已更新')
        return redirect(url_for('user.user_list'))
    return render_template('user_edit.html', user=user)

@user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('无权限')
        return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除')
    return redirect(url_for('user.user_list')) 