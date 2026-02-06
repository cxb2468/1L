from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import db
from app.models.user import User
from app.models.book import Book, Review
from app.models.order import Order, OrderItem

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
@login_required
def admin_required():
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('main.index'))


@admin_bp.route('/admin')
def admin_dashboard():
    # 获取统计信息
    total_books = Book.query.count()
    total_users = User.query.count()
    total_orders = Order.query.count()
    pending_reviews = Review.query.filter_by(approved=False).count()
    
    return render_template(
        'admin/dashboard.html',
        total_books=total_books,
        total_users=total_users,
        total_orders=total_orders,
        pending_reviews=pending_reviews
    )


@admin_bp.route('/admin/books')
def manage_books():
    page = request.args.get('page', 1, type=int)
    books = Book.query.paginate(page=page, per_page=10)
    return render_template('admin/books/manage.html', books=books)


@admin_bp.route('/admin/book/create', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        author = request.form.get('author')
        publisher = request.form.get('publisher')
        publication_date = request.form.get('publication_date')
        pages = request.form.get('pages', type=int)
        price = request.form.get('price', type=float)
        description = request.form.get('description')
        category = request.form.get('category')
        stock_quantity = request.form.get('stock_quantity', type=int, default=0)
        
        book = Book(
            isbn=isbn,
            title=title,
            author=author,
            publisher=publisher,
            pages=pages,
            price=price,
            description=description,
            category=category,
            stock_quantity=stock_quantity
        )
        
        if publication_date:
            from datetime import datetime
            book.publication_date = datetime.strptime(publication_date, '%Y-%m-%d')
        
        db.session.add(book)
        db.session.commit()
        
        flash('书籍已创建')
        return redirect(url_for('admin.manage_books'))
    
    return render_template('admin/books/create.html')


@admin_bp.route('/admin/book/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.isbn = request.form.get('isbn')
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.publisher = request.form.get('publisher')
        book.pages = request.form.get('pages', type=int)
        book.price = request.form.get('price', type=float)
        book.description = request.form.get('description')
        book.category = request.form.get('category')
        book.stock_quantity = request.form.get('stock_quantity', type=int, default=0)
        
        publication_date = request.form.get('publication_date')
        if publication_date:
            from datetime import datetime
            book.publication_date = datetime.strptime(publication_date, '%Y-%m-%d')
        
        db.session.commit()
        flash('书籍信息已更新')
        return redirect(url_for('admin.manage_books'))
    
    return render_template('admin/books/edit.html', book=book)


@admin_bp.route('/admin/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('书籍已删除')
    return redirect(url_for('admin.manage_books'))


@admin_bp.route('/admin/reviews')
def manage_reviews():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.paginate(page=page, per_page=10)
    return render_template('admin/reviews/manage.html', reviews=reviews)


@admin_bp.route('/admin/review/<int:review_id>/approve', methods=['POST'])
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.approved = True
    db.session.commit()
    flash('评论已批准')
    return redirect(url_for('admin.manage_reviews'))


@admin_bp.route('/admin/review/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('评论已删除')
    return redirect(url_for('admin.manage_reviews'))


@admin_bp.route('/admin/orders')
def manage_orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.paginate(page=page, per_page=10)
    return render_template('admin/orders/manage.html', orders=orders)


@admin_bp.route('/admin/order/<int:order_id>')
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/orders/detail.html', order=order)