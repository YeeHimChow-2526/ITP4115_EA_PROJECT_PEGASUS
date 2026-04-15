from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, FloatField, SelectField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('名', validators=[Length(max=50)])
    last_name = StringField('姓', validators=[Length(max=50)])
    phone = StringField('电话', validators=[Length(max=20)])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('用户名已存在')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('邮箱已被注册')

class LoginForm(FlaskForm):
    username = StringField('用户名/邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class ProductForm(FlaskForm):
    name = StringField('商品名称', validators=[DataRequired(), Length(max=200)])
    slug = StringField('URL标识', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('详细描述')
    short_description = StringField('简短描述', validators=[Length(max=500)])
    price = FloatField('售价', validators=[DataRequired(), NumberRange(min=0)])
    original_price = FloatField('原价', validators=[Optional(), NumberRange(min=0)])
    stock = IntegerField('库存', validators=[DataRequired(), NumberRange(min=0)])
    sku = StringField('SKU', validators=[Length(max=50)])
    brand = StringField('品牌', validators=[Length(max=100)])
    specifications = TextAreaField('规格参数(JSON格式)')
    category_id = SelectField('分类', coerce=int, validators=[DataRequired()])
    is_featured = BooleanField('设为推荐')
    is_new = BooleanField('设为新品')
    is_active = BooleanField('上架')
    image = FileField('商品图片')
    submit = SubmitField('保存')

class CartUpdateForm(FlaskForm):
    quantity = IntegerField('数量', validators=[DataRequired(), NumberRange(min=1, max=99)])
    submit = SubmitField('更新')

class CheckoutForm(FlaskForm):
    shipping_name = StringField('收货人姓名', validators=[DataRequired(), Length(max=100)])
    shipping_phone = StringField('联系电话', validators=[DataRequired(), Length(max=20)])
    shipping_address = TextAreaField('收货地址', validators=[DataRequired(), Length(max=300)])
    note = TextAreaField('订单备注')
    submit = SubmitField('提交订单')

class ProfileForm(FlaskForm):
    first_name = StringField('名', validators=[Length(max=50)])
    last_name = StringField('姓', validators=[Length(max=50)])
    phone = StringField('电话', validators=[Length(max=20)])
    address = TextAreaField('地址', validators=[Length(max=200)])
    submit = SubmitField('更新资料')