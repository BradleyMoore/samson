from flask_wtf import Form
from wtforms import BooleanField, PasswordField, TextField, validators


class LoginForm(Form):
    email = TextField('Email', [validators.Length(min=6, max=40), validators.Required()])
    password = PasswordField('Password', [validators.Length(min=5, max=128), validators.Required()])
    remember_me = BooleanField('Remember Me', default=False)

class RegisterForm(Form):
    email = TextField('Email', [validators.Length(min=6, max=40), validators.Required()])
    password = PasswordField('Password', [validators.Length(min=5, max=128), validators.Required()])
    username = TextField('Username', [validators.Length(min=4, max=32), validators.Required()])
    remember_me = BooleanField('Remember Me', default=False)
