from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, IPAddress, InputRequired 


class LoginForm(FlaskForm):
    cucm_ip = StringField('CUCM IP Address', default="10.50.4.20", validators=[DataRequired(), IPAddress()])
    cucm_username = StringField('CUCM Username', default="admin", validators=[DataRequired()])
    cucm_password = PasswordField('CUCM Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class DevicePool(FlaskForm):
    dp = SelectField('Select Device Pool')
    submit = SubmitField('Submit Selection')

class Users(FlaskForm):
    user = SelectField('Select a User', validators=[InputRequired()] )
    submit = SubmitField('Select User')

class User(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    display_name = StringField('Display Name')
    submit = SubmitField('Update User')


class UpdateUser(FlaskForm):
    submit = SubmitField('Change User')
