from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from app.models import db
from app.models.book import Book
from app.models.recently_viewed import RecentlyViewed

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # 获取推荐书籍（示例：随机推荐）
    books = Book.query.limit(12).all()
    
    # 如果用户已登录，获取最近浏览的项目
    recently_viewed = []
    if current_user.is_authenticated:
        recently_viewed_records = RecentlyViewed.query.filter_by(
            user_id=current_user.id
        ).order_by(
            RecentlyViewed.viewed_at.desc()
        ).limit(3).all()
        
        recently_viewed = [record.book for record in recently_viewed_records]
    
    return render_template('main/index.html', books=books, recently_viewed=recently_viewed)


@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        # 在书名、作者、ISBN中搜索
        books = Book.query.filter(
            db.or_(
                Book.title.contains(query),
                Book.author.contains(query),
                Book.isbn.contains(query)
            )
        ).paginate(page=page, per_page=12)
    else:
        books = Book.query.paginate(page=page, per_page=12)
    
    return render_template('main/search.html', books=books, query=query)