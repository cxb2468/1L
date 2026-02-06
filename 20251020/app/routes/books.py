from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import db
from app.models.book import Book, Review
from app.models.recently_viewed import RecentlyViewed

books_bp = Blueprint('books', __name__)


@books_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    
    # 获取该书的评论（仅已批准的）
    reviews = Review.query.filter_by(book_id=book_id, approved=True).all()
    
    # 如果用户已登录，记录最近浏览
    if current_user.is_authenticated:
        # 检查是否已存在最近浏览记录
        existing = RecentlyViewed.query.filter_by(
            user_id=current_user.id, 
            book_id=book_id
        ).first()
        
        if existing:
            # 更新时间戳
            existing.viewed_at = db.func.current_timestamp()
        else:
            # 创建新记录
            recently_viewed = RecentlyViewed(
                user_id=current_user.id,
                book_id=book_id
            )
            db.session.add(recently_viewed)
            
        db.session.commit()
    
    return render_template('books/detail.html', book=book, reviews=reviews)


@books_bp.route('/book/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')
    
    if not rating or rating < 1 or rating > 5:
        flash('请选择有效的评分 (1-5星)')
        return redirect(url_for('books.book_detail', book_id=book_id))
    
    # 创建评论（需要管理员批准）
    review = Review(
        rating=rating,
        comment=comment,
        user_id=current_user.id,
        book_id=book_id
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('评论已提交，等待管理员批准后显示')
    return redirect(url_for('books.book_detail', book_id=book_id))