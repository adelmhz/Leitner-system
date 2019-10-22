from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('این نام کاربری وجود دارد')

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('این ایمیل وجود دارد')

class RegisterForm(Form):
    name = StringField(
        'نام'
    )
    username = StringField(
        'نام کاربری',
        validators = [
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("نام کاربری فقط باید شامل یک کلمه، حرف، عدد و خط زیر باشد")

            ),
            name_exists
        ])
    email = StringField(
        'ایمیل',
        validators=[
            DataRequired(),
            Email(message='ایمیل نامعتبر است'),
            email_exists
        ])
    password = PasswordField(
        'رمز عبور',
        validators=[
            DataRequired(),
            Length(min=3, message="رمز عبور باید بیشتر ۳ کاراکتر باشد"),
            EqualTo('password2', message='رمز عبور با تکرار رمز عبور یکسان نیست')
        ])
    password2 = PasswordField(
        'تکرار رمز عبور',
        validators=[DataRequired()]
    )

class LoginForm(Form):
    email = StringField('ایمیل', validators=[DataRequired(), Email(message="ایمیل نامعتبر است")])
    password = PasswordField('رمز عبور', validators=[DataRequired()])