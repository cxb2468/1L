from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app.models import db
from app.models.book import Book
from app.models.cart import Cart, CartItem

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/cart')
@login_required
def view_cart():
    # 获取用户的购物车
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart:
        # 创建新的购物车
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    
    # 计算总计
    total = sum(item.book.price * item.quantity for item in cart_items)
    
    return render_template('cart/view.html', cart_items=cart_items, total=total)


@cart_bp.route('/cart/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    
    # 获取数量
    quantity = request.form.get('quantity', 1, type=int)
    
    # 获取或创建购物车
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    # 检查是否已在购物车中
    cart_item = CartItem.query.filter_by(
        cart_id=cart.id,
        book_id=book_id
    ).first()
    
    if cart_item:
        # 增加数量
        cart_item.quantity += quantity
    else:
        # 添加新项目
        cart_item = CartItem(
            cart_id=cart.id,
            book_id=book_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'已将 {book.title} 添加到购物车')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    # 确保用户只能删除自己购物车中的项目
    if cart_item.cart.user_id != current_user.id:
        flash('无法删除该商品')
        return redirect(url_for('cart.view_cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    
    flash('商品已从购物车中移除')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    # 确保用户只能更新自己购物车中的项目
    if cart_item.cart.user_id != current_user.id:
        flash('无法更新该商品')
        return redirect(url_for('cart.view_cart'))
    
    quantity = request.form.get('quantity', type=int)
    
    if quantity and quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
        flash('购物车已更新')
    else:
        flash('数量无效')
    
    return redirect(url_for('cart.view_cart'))