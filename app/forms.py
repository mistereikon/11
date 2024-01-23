import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length
from wtforms.validators import DataRequired, Length, EqualTo, Email
from __init__ import RegUser


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=4, max=10)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    about_me = StringField('About Me')  
    password = PasswordField('Password') 
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = RegUser.query.filter_by(RegName=username.data).first()
        if user and user.RegName != username.data:
            raise ValidationError('This username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = RegUser.query.filter_by(email=email.data).first()
        if user and user.email != email.data:
            raise ValidationError('This email is already registered. Please use a different one.')

