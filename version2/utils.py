# utils.py - 工具函数模块
import os
import uuid
import re
from datetime import datetime
from functools import wraps
from flask import session, current_app, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename
from models import db, Product, CartItem, User

# ---------- 购物车辅助函数 ----------
def get_cart_count():
    """获取当前购物车中的商品总数"""
    if current_user.is_authenticated:
        return CartItem.query.filter_by(user_id=current_user.id).count()
    else:
        cart = session.get('cart', {})
        return sum(cart.values())

def get_cart_items():
    """
    获取购物车中的商品详情和总金额
    返回: (items_list, total_price)
    items_list 中每个元素包含: id, product, quantity, subtotal
    """
    items = []
    total = 0.0
    
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for item in cart_items:
            if item.product and item.product.is_active:
                subtotal = item.product.price * item.quantity
                total += subtotal
                items.append({
                    'id': item.id,
                    'product': item.product,
                    'quantity': item.quantity,
                    'subtotal': subtotal
                })
    else:
        cart = session.get('cart', {})
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            if product and product.is_active:
                subtotal = product.price * quantity
                total += subtotal
                items.append({
                    'id': f"session_{product_id}",
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
    return items, total

def merge_cart():
    """用户登录时，将 session 购物车合并到数据库"""
    if current_user.is_authenticated:
        session_cart = session.pop('cart', {})
        for product_id, quantity in session_cart.items():
            product_id = int(product_id)
            cart_item = CartItem.query.filter_by(
                user_id=current_user.id, 
                product_id=product_id
            ).first()
            if cart_item:
                cart_item.quantity += quantity
            else:
                cart_item = CartItem(
                    user_id=current_user.id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(cart_item)
        db.session.commit()

def clear_cart():
    """清空当前用户的购物车"""
    if current_user.is_authenticated:
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
    else:
        session.pop('cart', None)

# ---------- 文件上传辅助函数 ----------
def allowed_file(filename):
    """检查文件扩展名是否允许上传"""
    if not filename:
        return False
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, subfolder=''):
    """
    保存上传的文件，返回保存的文件名（唯一）
    :param file: Flask 上传文件对象
    :param subfolder: 子文件夹名（可选）
    :return: 保存的文件名（不含路径），失败返回 None
    """
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_folder = os.path.join(upload_folder, subfolder)
        os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return unique_filename

def delete_uploaded_file(filename, subfolder=''):
    """删除上传的文件"""
    if not filename:
        return
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_folder = os.path.join(upload_folder, subfolder)
    filepath = os.path.join(upload_folder, filename)
    if os.path.exists(filepath):
        os.remove(filepath)

# ---------- 订单号生成 ----------
def generate_order_number(user_id):
    """
    生成唯一订单号
    格式: PEG + 年月日时分秒 + 用户ID + 4位随机字符
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = uuid.uuid4().hex[:4].upper()
    return f"PEG{timestamp}{user_id}{random_suffix}"

# ---------- 邮件发送（可选，需要配置） ----------
def send_email(recipient, subject, body, html=None):
    """
    发送邮件（需要配置邮件服务器）
    使用前需安装 flask-mail 并配置
    """
    try:
        from flask_mail import Mail, Message
        mail = Mail(current_app)
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        if html:
            msg.html = html
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"邮件发送失败: {e}")
        return False

def send_verification_email(user):
    """发送邮箱验证邮件"""
    from itsdangerous import URLSafeTimedSerializer
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='email-verify')
    verify_url = url_for('verify_email', token=token, _external=True)
    subject = "飞马电脑 - 邮箱验证"
    body = f"请点击以下链接验证您的邮箱：\n{verify_url}\n\n链接24小时内有效。"
    return send_email(user.email, subject, body)

def send_password_reset_email(user):
    """发送密码重置邮件"""
    from itsdangerous import URLSafeTimedSerializer
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='password-reset')
    reset_url = url_for('reset_password', token=token, _external=True)
    subject = "飞马电脑 - 密码重置"
    body = f"请点击以下链接重置密码：\n{reset_url}\n\n链接24小时内有效。"
    return send_email(user.email, subject, body)

# ---------- 数据验证辅助函数 ----------
def validate_phone(phone):
    """验证香港手机号码格式（简单示例）"""
    if not phone:
        return True
    # 香港手机: 5,6,9 开头，8位数字
    pattern = r'^[569]\d{7}$'
    return bool(re.match(pattern, phone))

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password_strength(password):
    """
    密码强度验证
    返回 (is_valid, message)
    """
    if len(password) < 6:
        return False, "密码长度至少6位"
    if len(password) > 50:
        return False, "密码长度不能超过50位"
    # 可选：要求包含数字和字母
    # if not re.search(r'[0-9]', password) or not re.search(r'[A-Za-z]', password):
    #     return False, "密码需包含字母和数字"
    return True, ""

# ---------- 分页辅助 ----------
def paginate(query, page, per_page, error_out=False):
    """简化的分页函数"""
    return query.paginate(page=page, per_page=per_page, error_out=error_out)

# ---------- 装饰器 ----------
def admin_required(f):
    """管理员权限装饰器（备用，实际在 admin.py 中已有）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- 日志记录（可选） ----------
def log_action(user_id, action, details=None):
    """
    记录用户操作日志（需要创建 Log 模型）
    此处仅作示例
    """
    # 如需实现，可创建 Log 模型并在此处添加记录
    pass