from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

# ============= Member 1: 用户认证与权限 (3张表) =============
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        return bcrypt.check_password_hash(self.password_hash, password)

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)  # JSON格式存储权限列表
    
    def get_permissions(self):
        return json.loads(self.permissions) if self.permissions else []
    
    def set_permissions(self, perm_list):
        self.permissions = json.dumps(perm_list)

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),)

# ============= Member 2: 商品管理 (3张表) =============
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 自引用关系
    parent = db.relationship('Category', remote_side=[id], backref='children')
    # 产品关系
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)  # 原价，用于显示折扣
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), unique=True)
    image_url = db.Column(db.String(500))
    image_filename = db.Column(db.String(200))
    brand = db.Column(db.String(100))
    specifications = db.Column(db.Text)  # JSON格式存储规格参数
    is_featured = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # 关系
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    
    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============= Member 3: 购物车与订单 (3张表) =============
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product'),)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.String(300), nullable=False)
    shipping_phone = db.Column(db.String(20), nullable=False)
    shipping_name = db.Column(db.String(100), nullable=False)
    payment_method = db.Column(db.String(50), default='cod')
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # 关系
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)  # 快照商品名称
    product_price = db.Column(db.Float, nullable=False)       # 快照商品价格
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

# ============= Member 4: 评价与浏览记录 (3张表) =============
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5星
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_review'),)

class BrowseHistory(db.Model):
    __tablename__ = 'browse_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_browse'),)

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_wishlist'),)