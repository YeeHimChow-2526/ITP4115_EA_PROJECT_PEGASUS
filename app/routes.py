import secrets

from functools import wraps
from datetime import datetime
from flask import render_template, redirect, flash, url_for, request, abort, make_response, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.email import send_password_reset_email
from app.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    PostForm,
    UserAdminForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    ProductForm,
    AddToCartForm,
    CheckoutForm,
    OrderSearchForm,
)
from app.models import (
    User,
    Post,
    ProductType,
    SaleType,
    Product,
    CartItem,
    Order,
    OrderItem,
)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.before_first_request
def initialize_shop():
    try:
        db.create_all()
    except Exception:
        pass

    try:
        if ProductType.query.count() == 0:
            types = [
                ProductType(name='CPU', description='Processors for your system'),
                ProductType(name='GPU', description='Graphics cards for gaming and rendering'),
                ProductType(name='Motherboard', description='Main boards for your PC'),
                ProductType(name='RAM', description='Memory modules'),
            ]
            db.session.add_all(types)
        if SaleType.query.count() == 0:
            sale_types = [
                SaleType(name='None', discount_percent=0, label='Regular Price'),
                SaleType(name='Clearance', discount_percent=20, label='Clearance Sale'),
                SaleType(name='Limited', discount_percent=10, label='Limited Offer'),
            ]
            db.session.add_all(sale_types)
        if User.query.filter_by(username='admin').first() is None:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
        db.session.commit()
    except Exception:
        db.session.rollback()


@app.context_processor
def inject_cart_count():
    cart_item_count = 0
    if current_user.is_authenticated:
        cart_item_count = sum(item.quantity for item in current_user.cart_items)
    return dict(cart_item_count=cart_item_count)

@app.route('/remember')
def remember():
    session['last_visited'] = 'admin'
    return redirect(url_for('index'))

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    type_id = request.args.get('type', type=int)
    query = Product.query.order_by(Product.name)

    if search:
        query = query.filter(
            Product.name.ilike(f'%{search}%') |
            Product.description.ilike(f'%{search}%')
        )
    if type_id:
        query = query.filter_by(type_id=type_id)

    products = query.paginate(page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    product_types = ProductType.query.order_by(ProductType.name).all()
    return render_template(
        'index.html.j2',
        title='Shop',
        products=products.items,
        product_types=product_types,
        pagination=products,
        search=search,
        selected_type=type_id,
    )


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Please login to add items to your cart.')
            return redirect(url_for('login'))
        if product.stock < form.quantity.data:
            flash('Not enough stock available.')
        else:
            item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
            if item:
                item.quantity += form.quantity.data
            else:
                item = CartItem(user=current_user, product=product, quantity=form.quantity.data)
                db.session.add(item)
            db.session.commit()
            flash('Product added to cart.')
            return redirect(url_for('cart'))
    return render_template('product.html.j2', title=product.name, product=product, form=form)


@app.route('/cart')
@login_required
def cart():
    items = current_user.cart_items.all()
    total = sum(item.total_price() for item in items)
    return render_template('cart.html.j2', title='Your Cart', items=items, total=total)


@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user != current_user:
        abort(403)
    if request.form.get('remove'):
        db.session.delete(item)
    else:
        quantity = request.form.get('quantity', type=int)
        if quantity is None or quantity < 1:
            db.session.delete(item)
        else:
            item.quantity = quantity
    db.session.commit()
    flash('Cart updated.')
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = current_user.cart_items.all()
    if not items:
        flash('Your cart is empty.')
        return redirect(url_for('index'))
    total = sum(item.total_price() for item in items)
    form = CheckoutForm()
    if form.validate_on_submit():
        order = Order(user=current_user, total_amount=total, shipping_address=form.shipping_address.data)
        db.session.add(order)
        db.session.commit()
        for item in items:
            order_item = OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            db.session.add(order_item)
            db.session.delete(item)
        db.session.commit()
        flash('Order placed successfully.')
        return redirect(url_for('orders'))
    return render_template('checkout.html.j2', title='Checkout', items=items, total=total, form=form)


@app.route('/orders')
@login_required
def orders():
    orders = current_user.orders.order_by(Order.created_at.desc()).all()
    return render_template('orders.html.j2', title='Your Orders', orders=orders)


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user != current_user:
        abort(403)
    return render_template('order_detail.html.j2', title=f'Order #{order.id}', order=order)


@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html.j2', title='Admin Dashboard')


@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users.html.j2', title='Admin Users', users=users)


@app.route('/admin/user/new', methods=['GET', 'POST'])
@admin_required
def add_user():
    form = UserAdminForm(original_username='', original_email='')
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            about_me=form.about_me.data,
            is_admin=form.is_admin.data,
        )
        user.set_password(secrets.token_urlsafe(12))
        db.session.add(user)
        db.session.commit()
        flash('User created successfully. They can reset their password through the normal reset flow.')
        return redirect(url_for('admin_users'))
    return render_template('admin/add_user.html.j2', title='Add User', form=form)


@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserAdminForm(original_username=user.username, original_email=user.email, obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)
        user.about_me = form.about_me.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('admin_users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.about_me.data = user.about_me
        form.is_admin.data = user.is_admin
    return render_template('admin/edit_user.html.j2', title='Edit User', form=form, user=user)


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.')
    return redirect(url_for('admin_users'))


@app.route('/admin/products')
@admin_required
def admin_products():
    products = Product.query.order_by(Product.name).all()
    return render_template('admin/products.html.j2', title='Admin Products', products=products)


@app.route('/admin/product/new', methods=['GET', 'POST'])
@admin_required
def add_product():
    form = ProductForm()
    form.type_id.choices = [(ptype.id, ptype.name) for ptype in ProductType.query.order_by(ProductType.name).all()]
    form.sale_type_id.choices = [(stype.id, stype.name) for stype in SaleType.query.order_by(SaleType.name).all()]
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            is_on_sale=form.is_on_sale.data,
            type_id=form.type_id.data,
            sale_type_id=form.sale_type_id.data,
            image_url=form.image_url.data,
        )
        db.session.add(product)
        db.session.commit()
        flash('Product created successfully.')
        return redirect(url_for('admin_products'))
    return render_template('admin/add_product.html.j2', title='Add Product', form=form)


@app.route('/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.type_id.choices = [(ptype.id, ptype.name) for ptype in ProductType.query.order_by(ProductType.name).all()]
    form.sale_type_id.choices = [(stype.id, stype.name) for stype in SaleType.query.order_by(SaleType.name).all()]
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.is_on_sale = form.is_on_sale.data
        product.type_id = form.type_id.data
        product.sale_type_id = form.sale_type_id.data
        product.image_url = form.image_url.data
        db.session.commit()
        flash('Product updated successfully.')
        return redirect(url_for('admin_products'))
    if request.method == 'GET':
        form.type_id.data = product.type_id
        form.sale_type_id.data = product.sale_type_id
    return render_template('admin/edit_product.html.j2', title='Edit Product', form=form, product=product)


@app.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product removed successfully.')
    return redirect(url_for('admin_products'))


@app.route('/admin/orders', methods=['GET', 'POST'])
@admin_required
def admin_orders():
    form = OrderSearchForm()
    search_query = request.args.get('search', '', type=str)
    orders_query = Order.query.order_by(Order.created_at.desc())
    
    if request.method == 'POST' and form.search.data:
        search_query = form.search.data
    
    if search_query:
        # Try to search by order ID first
        try:
            order_id = int(search_query)
            orders_query = orders_query.filter(Order.id == order_id)
        except ValueError:
            # If not a valid integer, search by user ID
            try:
                user_id = int(search_query)
                orders_query = orders_query.filter(Order.user_id == user_id)
            except ValueError:
                # If neither, search by username
                orders_query = orders_query.join(User).filter(User.username.ilike(f'%{search_query}%'))
    
    orders = orders_query.all()
    return render_template('admin/orders.html.j2', title='Admin Orders', orders=orders, form=form, search=search_query)


@app.route('/admin/order/<int:order_id>')
@admin_required
def order_detail_admin(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html.j2', title=f'Order #{order.id}', order=order)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html.j2', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html.j2', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html.j2', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if user is None:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html.j2', title='Reset Password', form=form)


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html.j2', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html.j2', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}!')
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}!')
    return redirect(url_for('user', username=username))
