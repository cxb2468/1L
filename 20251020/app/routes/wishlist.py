from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import db
from app.models.book import Book
from app.models.wishlist import Wishlist, WishlistItem
from app.models.cart import Cart, CartItem

wishlist_bp = Blueprint('wishlist', __name__)


@wishlist_bp.route('/wishlists')
@login_required
def my_wishlists():
    wishlists = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist/my_wishlists.html', wishlists=wishlists)


@wishlist_bp.route('/wishlists/public')
def public_wishlists():
    wishlists = Wishlist.query.filter_by(is_public=True).all()
    return render_template('wishlist/public_wishlists.html', wishlists=wishlists)


@wishlist_bp.route('/wishlist/create', methods=['GET', 'POST'])
@login_required
def create_wishlist():
    if request.method == 'POST':
        name = request.form.get('name')
        is_public = bool(request.form.get('is_public'))
        
        wishlist = Wishlist(
            name=name,
            is_public=is_public,
            user_id=current_user.id
        )
        
        db.session.add(wishlist)
        db.session.commit()
        
        flash('愿望清单已创建')
        return redirect(url_for('wishlist.my_wishlists'))
    
    return render_template('wishlist/create.html')


@wishlist_bp.route('/wishlist/<int:wishlist_id>')
def view_wishlist(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    # 检查访问权限
    if not wishlist.is_public and (
            not current_user.is_authenticated or 
            current_user.id != wishlist.user_id):
        flash('无法访问该愿望清单')
        return redirect(url_for('wishlist.my_wishlists'))
    
    return render_template('wishlist/view.html', wishlist=wishlist)


@wishlist_bp.route('/wishlist/<int:wishlist_id>/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_wishlist(wishlist_id, book_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    book = Book.query.get_or_404(book_id)
    
    # 确保用户只能向自己的愿望清单添加书籍
    if wishlist.user_id != current_user.id:
        flash('无法向该愿望清单添加书籍')
        return redirect(url_for('wishlist.my_wishlists'))
    
    # 检查是否已在愿望清单中
    existing_item = WishlistItem.query.filter_by(
        wishlist_id=wishlist_id,
        book_id=book_id
    ).first()
    
    if existing_item:
        flash('书籍已在愿望清单中')
    else:
        wishlist_item = WishlistItem(
            wishlist_id=wishlist_id,
            book_id=book_id
        )
        db.session.add(wishlist_item)
        db.session.commit()
        flash(f'已将 {book.title} 添加到愿望清单')
    
    return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist_id))


@wishlist_bp.route('/wishlist/<int:wishlist_id>/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_wishlist(wishlist_id, item_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    # 确保用户只能从自己的愿望清单中移除书籍
    if wishlist.user_id != current_user.id:
        flash('无法从该愿望清单中移除书籍')
        return redirect(url_for('wishlist.my_wishlists'))
    
    wishlist_item = WishlistItem.query.get_or_404(item_id)
    db.session.delete(wishlist_item)
    db.session.commit()
    
    flash('书籍已从愿望清单中移除')
    return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist_id))


@wishlist_bp.route('/wishlist/<int:wishlist_id>/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_wishlist_item_to_cart(wishlist_id, book_id):
    # 注意：这里允许用户将任何公开愿望清单中的书籍添加到购物车
    book = Book.query.get_or_404(book_id)
    
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
        cart_item.quantity += 1
    else:
        # 添加新项目
        cart_item = CartItem(
            cart_id=cart.id,
            book_id=book_id,
            quantity=1
        )
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'已将 {book.title} 添加到购物车')
    
    return redirect(url_for('cart.view_cart'))