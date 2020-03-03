from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    cucm_username = StringField('CUCM Username', validators=[DataRequired()])
    password = PasswordField('CUCM Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')