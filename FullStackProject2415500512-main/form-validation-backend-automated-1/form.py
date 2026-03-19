from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, SubmitField
from wtforms import validators


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired(), validators.Length(min=4, max=25)])
    email = EmailField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = StringField('Password', validators=[validators.DataRequired(), validators.Length(min=6)])
    confirm_password = StringField('Confirm Password', validators=[validators.DataRequired(), validators.EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')