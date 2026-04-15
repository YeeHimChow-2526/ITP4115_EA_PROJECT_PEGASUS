# admin.py - 完整后台管理模块
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, User, Product, Category, Order, OrderItem
from forms import ProductForm
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ---------- 辅助函数 ----------
def admin_required(func):
    """管理员权限装饰器"""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def allowed_file(filename):
    """检查文件扩展名是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# ---------- 仪表板 ----------
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders)

# ---------- 用户管理 ----------
@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    role = request.args.get('role', 'all')
    
    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search),
                User.phone.contains(search)
            )
        )
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    if role == 'admin':
        query = query.filter_by(is_admin=True)
    elif role == 'user':
        query = query.filter_by(is_admin=False)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    users = pagination.items
    
    return render_template('admin/users.html', 
                         users=users, 
                         pagination=pagination,
                         search=search,
                         status=status,
                         role=role)

@admin_bp.route('/users/edit', methods=['POST'])
@login_required
@admin_required
def edit_user():
    user_id = request.form.get('user_id')
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('不能修改自己的帳戶權限', 'danger')
        return redirect(url_for('admin.admin_users'))
    
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    user.first_name = request.form.get('first_name', '')
    user.last_name = request.form.get('last_name', '')
    user.phone = request.form.get('phone', '')
    user.address = request.form.get('address', '')
    user.is_admin = request.form.get('is_admin') == 'on'
    user.is_active = request.form.get('is_active') == 'on'
    
    new_password = request.form.get('new_password')
    if new_password:
        user.set_password(new_password)
    
    db.session.commit()
    flash(f'用戶 {user.username} 資料已更新', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': '不能刪除自己'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

# ---------- 商品管理 ----------
@admin_bp.route('/products')
@login_required
@admin_required
def admin_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', 'all')
    status = request.args.get('status', 'all')
    
    query = Product.query
    if search:
        query = query.filter(
            db.or_(
                Product.name.contains(search),
                Product.sku.contains(search),
                Product.brand.contains(search)
            )
        )
    if category_id != 'all':
        query = query.filter_by(category_id=int(category_id))
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    products = pagination.items
    categories = Category.query.all()
    
    return render_template('admin/products.html', 
                         products=products,
                         pagination=pagination,
                         categories=categories,
                         search=search,
                         category_id=category_id,
                         status=status)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    form.category_id.choices = [(0, '請選擇分類')] + [(c.id, c.name) for c in Category.query.order_by(Category.sort_order).all()]
    
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                image_file.save(filepath)
                image_filename = unique_filename
        
        product = Product(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            short_description=form.short_description.data,
            price=form.price.data,
            original_price=form.original_price.data or None,
            stock=form.stock.data,
            sku=form.sku.data,
            brand=form.brand.data,
            specifications=form.specifications.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            is_featured=form.is_featured.data,
            is_new=form.is_new.data,
            is_active=form.is_active.data,
            image_filename=image_filename
        )
        db.session.add(product)
        db.session.commit()
        flash('商品添加成功', 'success')
        return redirect(url_for('admin.admin_products'))
    
    return render_template('admin/product_form.html', form=form, title='新增商品')

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(0, '請選擇分類')] + [(c.id, c.name) for c in Category.query.order_by(Category.sort_order).all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.slug = form.slug.data
        product.description = form.description.data
        product.short_description = form.short_description.data
        product.price = form.price.data
        product.original_price = form.original_price.data or None
        product.stock = form.stock.data
        product.sku = form.sku.data
        product.brand = form.brand.data
        product.specifications = form.specifications.data
        product.category_id = form.category_id.data if form.category_id.data != 0 else None
        product.is_featured = form.is_featured.data
        product.is_new = form.is_new.data
        product.is_active = form.is_active.data
        
        if form.image.data and form.image.data.filename:
            image_file = form.image.data
            if allowed_file(image_file.filename):
                if product.image_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(image_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                image_file.save(filepath)
                product.image_filename = unique_filename
        
        db.session.commit()
        flash('商品更新成功', 'success')
        return redirect(url_for('admin.admin_products'))
    
    return render_template('admin/product_form.html', form=form, title='編輯商品', product=product)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.image_filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/products/batch', methods=['POST'])
@login_required
@admin_required
def batch_products():
    action = request.form.get('action')
    product_ids = request.form.get('product_ids', '')
    ids = [int(id) for id in product_ids.split(',') if id.isdigit()]
    
    if not ids:
        flash('未選擇商品', 'danger')
        return redirect(url_for('admin.admin_products'))
    
    products = Product.query.filter(Product.id.in_(ids)).all()
    
    if action == 'delete':
        for p in products:
            if p.image_filename:
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], p.image_filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            db.session.delete(p)
        flash(f'已刪除 {len(products)} 件商品', 'success')
    elif action == 'activate':
        for p in products:
            p.is_active = True
        flash(f'已上架 {len(products)} 件商品', 'success')
    elif action == 'deactivate':
        for p in products:
            p.is_active = False
        flash(f'已下架 {len(products)} 件商品', 'success')
    elif action == 'feature':
        for p in products:
            p.is_featured = True
        flash(f'已設為推薦 {len(products)} 件商品', 'success')
    elif action == 'unfeature':
        for p in products:
            p.is_featured = False
        flash(f'已取消推薦 {len(products)} 件商品', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.admin_products'))

# ---------- 订单管理 ----------
@admin_bp.route('/orders')
@login_required
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/orders/update/<int:order_id>/<status>')
@login_required
@admin_required
def update_order_status(order_id, status):
    order = Order.query.get_or_404(order_id)
    valid_status = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']
    if status in valid_status:
        order.status = status
        from datetime import datetime
        if status == 'paid':
            order.paid_at = datetime.utcnow()
        elif status == 'shipped':
            order.shipped_at = datetime.utcnow()
        elif status == 'delivered':
            order.delivered_at = datetime.utcnow()
        db.session.commit()
        flash(f'訂單 #{order.order_number} 狀態已更新為 {status}', 'success')
    return redirect(url_for('admin.admin_orders'))

# ---------- 分类管理 ----------
@admin_bp.route('/categories')
@login_required
@admin_required
def admin_categories():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name')
    slug = request.form.get('slug')
    if name and slug:
        # 检查是否已存在
        existing = Category.query.filter_by(slug=slug).first()
        if existing:
            flash('分類 URL 已存在', 'danger')
        else:
            category = Category(name=name, slug=slug, sort_order=Category.query.count())
            db.session.add(category)
            db.session.commit()
            flash('分類添加成功', 'success')
    return redirect(url_for('admin.admin_categories'))

@admin_bp.route('/categories/delete/<int:category_id>')
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products:
        flash('該分類下有商品，無法刪除', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('分類已刪除', 'success')
    return redirect(url_for('admin.admin_categories'))

@admin_bp.route('/categories/update', methods=['POST'])
@login_required
@admin_required
def update_category():
    category_id = request.form.get('category_id')
    category = Category.query.get_or_404(category_id)

    category.name = request.form.get('name')
    category.slug = request.form.get('slug')
    parent_id = request.form.get('parent_id')
    category.parent_id = int(parent_id) if parent_id and parent_id != '' else None
    category.sort_order = request.form.get('sort_order', 0, type=int)
    category.is_active = request.form.get('is_active') == '1'

    # 防止将分类自身设为上级
    if category.parent_id == category.id:
        category.parent_id = None

    db.session.commit()
    flash(f'分類 {category.name} 已更新', 'success')
    return redirect(url_for('admin.admin_categories'))