from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import *


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterNode(FlaskForm):
    nodeName = StringField('Node name:', validators=[DataRequired()])
    nodeLocation = StringField('Location:', validators=[DataRequired()])
    nodeAdd = SubmitField('Add Node')

    nodeView = SubmitField('View Token')
    nodeRemove = SubmitField('Remove Node')


class UserManagement(FlaskForm):
    userRemove = SubmitField('Remove User')