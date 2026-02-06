from app import db
from app.models.book import Book
from app.models.order import OrderItem
from sqlalchemy import func


def get_category_recommendations(category, limit=5):
    """
    根据类别推荐书籍
    """
    recommendations = Book.query.filter_by(category=category).limit(limit).all()
    return recommendations


def get_popular_books(limit=10):
    """
    获取热门书籍（按销量排序）
    """
    popular_books = db.session.query(Book).join(
        OrderItem, Book.id == OrderItem.book_id
    ).group_by(
        Book.id
    ).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(limit).all()
    
    return popular_books


def get_similar_books(book, limit=5):
    """
    根据相同类别推荐相似书籍
    """
    similar_books = Book.query.filter(
        Book.category == book.category,
        Book.id != book.id
    ).limit(limit).all()
    
    return similar_books


def get_personalized_recommendations(user, limit=10):
    """
    根据用户购买历史推荐书籍
    """
    # 这是一个简化的实现，实际应用中可能需要更复杂的算法
    # 例如基于协同过滤或内容推荐
    
    # 获取用户购买过的书籍类别
    user_categories = db.session.query(Book.category).join(
        OrderItem, Book.id == OrderItem.book_id
    ).join(
        # 这里需要连接订单表，但为了简化示例，我们只展示思路
        # 实际实现需要连接 Order 表和 User 表
    ).filter(
        # Order.user_id == user.id
    ).distinct().all()
    
    # 基于类别推荐书籍
    if user_categories:
        category_list = [cat[0] for cat in user_categories]
        recommendations = Book.query.filter(
            Book.category.in_(category_list)
        ).limit(limit).all()
        return recommendations
    
    # 如果没有购买历史，推荐热门书籍
    return get_popular_books(limit)