from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, IPAddress


class LoginForm(FlaskForm):
    cucm_ip = StringField('CUCM IP Address', validators=[DataRequired(), IPAddress()])
    cucm_username = StringField('CUCM Username', validators=[DataRequired()])
    cucm_password = PasswordField('CUCM Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
