from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange, Optional
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField("Request Password Reset")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")


class PostForm(FlaskForm):
    post = TextAreaField("Say Something", validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField("Submit")


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(max=140)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)], places=2)
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    is_on_sale = BooleanField("On Sale")
    type_id = SelectField("Product Type", coerce=int, validators=[DataRequired()])
    sale_type_id = SelectField("Sale Type", coerce=int, validators=[DataRequired()])
    image_url = StringField("Image URL", validators=[Optional(), Length(max=200)])
    submit = SubmitField("Save Product")


class AddToCartForm(FlaskForm):
    quantity = IntegerField("Quantity", default=1, validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Add to Cart")


class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField("Shipping Address", validators=[DataRequired(), Length(max=200)])
    submit = SubmitField("Place Order")
