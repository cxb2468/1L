from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import db
from app.models.book import Book
from app.models.order import Order, OrderItem
from sqlalchemy import func
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)


@reports_bp.before_request
@login_required
def report_access_required():
    if not current_user.is_admin and not current_user.is_report_viewer:
        flash('需要报表查看权限')
        return redirect(url_for('main.index'))


@reports_bp.route('/reports')
def reports_dashboard():
    return render_template('reports/dashboard.html')


@reports_bp.route('/reports/daily')
def daily_report():
    # 获取今天的日期
    today = datetime.utcnow().date()
    
    # 获取今天的订单统计
    daily_orders = db.session.query(
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('total_revenue')
    ).filter(
        func.date(Order.order_date) == today
    ).first()
    
    # 获取按类别分组的销售数据
    category_sales = db.session.query(
        Book.category,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue')
    ).join(
        OrderItem, Book.id == OrderItem.book_id
    ).join(
        Order, OrderItem.order_id == Order.id
    ).filter(
        func.date(Order.order_date) == today
    ).group_by(
        Book.category
    ).all()
    
    # 获取畅销书排行
    best_sellers = db.session.query(
        Book.title,
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(
        OrderItem, Book.id == OrderItem.book_id
    ).join(
        Order, OrderItem.order_id == Order.id
    ).filter(
        func.date(Order.order_date) == today
    ).group_by(
        Book.id, Book.title
    ).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()
    
    # 获取滞销书（90天内未销售）
    ninety_days_ago = today - timedelta(days=90)
    slow_movers = db.session.query(
        Book.title,
        Book.stock_quantity
    ).outerjoin(
        OrderItem, Book.id == OrderItem.book_id
    ).outerjoin(
        Order, OrderItem.order_id == Order.id
    ).filter(
        (Order.order_date < ninety_days_ago) | (Order.id.is_(None))
    ).limit(10).all()
    
    return render_template(
        'reports/daily.html',
        daily_orders=daily_orders,
        category_sales=category_sales,
        best_sellers=best_sellers,
        slow_movers=slow_movers,
        report_date=today
    )